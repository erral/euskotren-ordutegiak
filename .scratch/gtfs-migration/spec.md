# GTFS migration specification

Status: written 2026-11-25. Implementation is a separate effort.

## Purpose

Replace the PDF static pipeline with Euskotren GTFS as the source of truth for the published timetable, while preserving the current four lines, workbook and wide HTML outputs. The PDF pipeline remains the validation/provenance and reference build.

## Scope

In scope:

- the GTFS adapter and its mapping into `Service` / `StopTime`;
- route and direction filtering for E1, E2-T1, E4 and E3-L3;
- service identity, deduplication and `WD/SA/SU/WE/FN/SN` calendar derivation;
- the GTFS parent-station to canonical-stop alias table;
- the hard PDF-diff validation contract;
- build, manifest, refresh cadence, staleness gate and rollout;
- the CC BY 4.0 licence and attribution requirements.

Out of scope:

- E3a (Lutxana–Sondika), date-specific calendars/date picker and new user-facing views;
- real-time GTFS-RT/SIRI integration;
- trams, the funicular and non-Euskotren operators;
- changing the wide workbook/HTML output shape;
- implementing the migration itself; this document is the handoff.

## Source contract

- Discovery index: `https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/data-index.json`, key `data.Euskotren`.
- GTFS static feed: `https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip`.
- The feed is a rolling window. At the evaluation date it was `2026-11-25 → 2026-12-30`, version `20261125043408`, published daily around 07:00 Europe/Madrid.
- The feed is licensed **CC BY 4.0** (see [Licence and attribution](#licence-and-attribution)).
- The adapter must accept a local GTFS zip path; the workflow downloads the feed itself.
- The feed may contain E1, E3, E3a, E4, L3, T0, T1, the trams, the funicular and FCC. Only the six rail routes mapped below are in scope.

## Model mapping

The adapter produces `list[Service]` and `GtfsFeedMeta`; the workbook, site, service-order and corridor modules stay unchanged.

### Service

| Field | GTFS mapping |
|---|---|
| `service_id` | Public scheme `<line>-<direction>-<calendar>-<departure>` |
| `primary_line` | Mapped line from the route table |
| `pattern` | `night` for FN/SN, otherwise `through` or `short-turn` |
| `direction` | Mapped direction from the trip endpoints |
| `calendar` | Mapped `WD/SA/SU/WE/FN/SN` |
| `valid_from` | Feed `feed_start_date` |
| `valid_to` | Feed `feed_end_date` |
| `origin` / `destination` | First/last served canonical stop |
| `departure` / `arrival` | First departure / last arrival |
| `source_pdf` | GTFS source URL or feed identifier, kept for compatibility |
| `frequency_rule_ids` | Empty; GTFS trips are already explicit |
| `notes` | Empty except for documented mapping corrections; provenance lives in the sidecar fields |
| `appears_in` | Computed by `assign_membership` |
| `gtfs_trip_id` | Optional new field: GTFS trip ID |
| `gtfs_service_id` | Optional new field: GTFS service ID |

### StopTime

| Field | GTFS mapping |
|---|---|
| `stop_id` / `stop_name` | Canonical stop resolved through the alias table |
| `sequence` | Canonical line stop-order position, 1..N |
| `time` | GTFS `departure_time` |
| `disposition` | `stop` for a GTFS call, `not_served` for an omitted stop |
| `source` | `gtfs` |
| `day_offset` | Derived from the GTFS service day/extended clock |

The service is expanded to the full canonical stop list for its mapped line/direction; omitted stops become `not_served`. GTFS has no `unpublished` `?` state and no PDF `pass` marker. `pickup_type` / `drop_off_type` are ignored in the first migration.

### Pattern

- FN/SN services: `["night"]`.
- Otherwise `["through"]` when the trip serves both endpoints of the mapped line's canonical stop list, else `["short-turn"]`.
- `refuerzo`-only labels are not recreated; this is a documented presentation difference.

## GTFS adapter

- New module: `euskotren_timetable/gtfs.py`.
- Uses standard-library `zipfile` and `csv`; no new runtime dependency.
- Entry point: `load_gtfs_services(zip_path, ...) -> tuple[list[Service], GtfsFeedMeta]`.
- The adapter reads `agency`, `routes`, `trips`, `stops`, `stop_times`, `calendar`, `calendar_dates` and `feed_info`.
- `GtfsFeedMeta` carries at least: `source_url`, `sha256`, `feed_version`, `feed_start_date`, `feed_end_date`, `fetched_at`, `publisher`, `licence`.
- The adapter reuses `assign_membership`; it does not compute corridor membership itself.
- The existing PDF parsers remain untouched.

## Route and direction mapping

| GTFS route | Current line | Direction source |
|---|---|---|
| `E1` | E1 | E1 canonical stop order |
| `E4` | E4 | E4 canonical stop order |
| `E3` | E3-L3 | E3 canonical order (`Lezama-Kukullaga` / `Kukullaga-Lezama`) |
| `L3` | E3-L3 | L3 canonical order (`Matiko-Kukullaga` / `Kukullaga-Matiko`) |
| `T0` | E2-T1 | E2-T1 canonical order |
| `T1` | E2-T1 | E2-T1 canonical order |

`E3a`, `FE`, `TG1`, `TG2`, `TR`, `41` and `FCC` are excluded.

Direction is the canonical direction whose stop order matches the trip's first/last stop positions. T0/T1 are merged under E2-T1; E3/L3 under E3-L3.

## Service identity and deduplication

- Public IDs preserve the current `<line>-<direction>-<calendar>-<departure>` scheme.
- GTFS `trip_id`/`service_id` are provenance, not public identity.
- Deduplicate to one `Service` per `(primary_line, direction, calendar, departure)`.
- Duplicate GTFS trips are collapsed only when they are equivalent after mapping (same served stops and times). If two trips share the key but differ, fail and report; do not silently pick one.
- IDs are time-dependent and change when the timetable changes; no cross-feed stability guarantee. HTML anchors inherit that behaviour.

## Calendar derivation

Preserve the current per-line calendar sets:

| Line | Calendars |
|---|---|
| E1 | `WD`, `SA`, `SU`, `WE`, `SN` |
| E2-T1 | `WD`, `SA`, `SU`, `WE`, `SN` |
| E4 | `WD`, `SU`, `WE`, `SN` |
| E3-L3 | `WD`, `WE`, `FN`, `SN` |

The adapter derives candidate calendars from representative dates inside the feed window and filters them to this table.

Representative-date algorithm:

1. Choose the first date in the feed window for the target weekday that has no `calendar_dates` exception and lies within the active range of the relevant service IDs.
2. `WD`: union of a normal Monday–Thursday date and a normal Friday date, deduplicated.
3. `SA`: normal Saturday. `SU`: normal Sunday. `WE`: union of the `SA` and `SU` trip sets for lines that publish `WE`.
4. `FN`: trips active on the representative Friday service day with at least one stop time at or after `24:00`.
5. `SN`: trips active on the representative Saturday service day with at least one stop time at or after `24:00`.
6. Record the chosen dates in the GTFS manifest.

For the 2026-11-25 feed the natural candidate dates are 2026-11-25/27 (weekday), 2026-11-28 (Saturday), 2026-11-29 (Sunday), 2026-11-27 (Friday night) and 2026-11-28 (Saturday night); the implementation must recompute them from each feed.

`calendar_dates` holiday exceptions are ignored for the first migration and retained in the adapter for the later date-aware view.

## Stop alias mapping

- New module: `euskotren_timetable/gtfs_stops.py`.
- Map GTFS `parent_station` IDs (location type 1, `StopPlace`) to canonical names, with the GTFS name recorded for diagnostics.
- Resolve every `stop_times.stop_id` to its parent station before mapping.
- Ignore Quay/platform, entrance and generic-node records.
- Keep `STOP_REGISTRY`, canonical names and display order unchanged.
- E3a stops are out of scope; extend the registry/alias table only if E3a is added later.
- Hard validation: every in-scope GTFS parent station maps exactly once; every canonical stop used by the four lines has a mapping. No fuzzy matching at runtime.
- Known many-to-one cases (if any) must be explicit and reviewed, not accidental.

## Validation and PDF diff

- Reference: the pinned PDF-derived build from `data/manifest.json` and the current parsers.
- Build both sources in CI and compare the overlapping services and calendars.
- Compare by `(primary_line, direction, calendar, departure)` and by canonical stop.
- Hard failures:
  - missing or extra services;
  - different displayed departure times;
  - different served/`not_served` sets;
  - duplicate public IDs;
  - unmapped GTFS trips or stops;
  - a PDF known time that GTFS does not publish.
- `Service.arrival`: compare against the last displayed departure via the terminal-stop rule; report a GTFS arrival difference separately rather than failing when the departure matches.
- Presentation differences:
  - PDF `pass` (`>`) becomes blank; the marker is retired.
  - PDF `?` may become a GTFS time; report these as improvements and require an explicit allowlist entry.
  - `pattern`, `notes`, `source_pdf`, `frequency_rule_ids`, validity metadata and the `refuerzo` label are not part of the timetable equality gate.
- Allowlist: `data/gtfs-pdf-allowlist.yaml`, initially empty; every entry names the service/field, the reason and the review date. No silent tolerance.
- Diff report: a human-readable `added / removed / changed` report produced as a CI artifact.
- Golden tests: Arroa 06:53, E1 05:35, representative E2/E3/E4 services and the night calendars.
- Holiday exceptions are excluded from the first comparison; record the limitation in the report.

## Build and manifest

- CLI: `build-html --source gtfs|pdf --gtfs <zip>`; `pdf` remains the default until cutover.
- The GTFS path builds the same workbook and site from `load_gtfs_services`; the PDF path remains the reference/validation build.
- Generate `data/gtfs-manifest.json` inside each GTFS site's `data/` directory with the feed metadata and SHA-256.
- Add an optional `gtfs` object to `data/services.json` meta with the feed version/window/source/checksum.
- Carry the feed version/window/licence into the site footer and workbook metadata.
- Do not commit a new manifest daily; the deployed artifact is the record. Keep a committed schema/example.
- Keep the PDF manifest and PDF download path for validation.
- The Frequency rules sheet remains but has no GTFS rules; GTFS trips are explicit.
- The Master `Source PDF` column becomes `Source` and shows the GTFS source/feed identifier.

## Workflow, parallel publication and rollout

### Daily workflow

- Extend `.github/workflows/tests.yml` with a daily schedule after the feed's ~07:00 local publication (for example 06:30 UTC).
- Download the GTFS zip and the pinned PDFs.
- Compute/check the feed metadata; fail when the feed is missing, the download fails, or fewer than **7 days** remain in `feed_end_date`.
- Build the GTFS site/workbook and the PDF reference; run the hard diff.
- Publish only on success; a failed run leaves the last successful Pages deployment live.
- Keep the push/PR/manual test job and the PDF download for the diff.

### One-week parallel publication

During the soak:

- `/` remains the PDF-derived site.
- `/gtfs/` is the GTFS preview, self-contained, linked from `/` with a visible “GTFS preview” banner/label.
- Both workbook variants are public: `…_pdf.xlsx` and `…_gtfs.xlsx`.
- The daily workflow updates `/gtfs/` only when the hard diff passes.

After one week of clean daily runs:

- GTFS becomes the canonical site at `/`.
- The PDF build is retired from public publication but remains the CI validation/reference build.
- The canonical workbook download becomes the GTFS workbook.

### Attribution at cutover

Add the CC BY 4.0 attribution to the README, site footer and workbook metadata: credit Eusko Trenbideak, link the GTFS source and the CC BY 4.0 licence, note that the data was transformed, and include the feed version/last-update date.

## Licence and attribution

- Licence: **CC BY 4.0** for the dataset. The feed itself has no licence file/field; the licence comes from the Open Data Euskadi catalogue record (dataset card, DCAT RDF, schema.org JSON-LD).
- Redistribution and derivative works are allowed. Required: attribution, source and licence links, change notice, last-update/feed version.
- Publish the derived workbook/HTML/JSON under **CC BY 4.0**; keep the generator code under **GPL-2.0**.
- Sample notice:

  > Timetable data: Eusko Trenbideak / Euskotren, via Open Data Euskadi (Moveuskadi), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source: [GTFS feed](https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip), feed version `<version>`, last updated `<date>`. Changes: transformed into this Excel workbook and HTML timetable. Derived timetable data is published under CC BY 4.0; the generator code is GPL-2.0.

## Testing

Unit tests:

- route and direction mapping;
- stop alias coverage and uniqueness;
- departure-time and `not_served` mapping;
- deduplication and public-ID generation;
- calendar derivation and per-line filtering;
- FN/SN classification and extended times;
- provenance fields and feed metadata.

Integration tests:

- build from a fixture GTFS zip;
- build the PDF reference and run the diff;
- site link/JSON validation;
- golden Arroa/E1/E2/E3/E4/night services;
- staleness gate and missing-feed failure.

The hard PDF diff is part of the release gate, not merely a local check.

## Implementation boundary

In the first migration:

- four lines: E1, E2-T1 (T0+T1), E4, E3-L3 (E3+L3);
- current per-line calendar sets;
- current workbook and wide HTML shapes;
- daily GTFS refresh with a 7-day staleness floor;
- one-week `/` vs `/gtfs/` parallel publication;
- CC BY 4.0 attribution.

Deferred:

- E3a Lutxana–Sondika;
- date-specific calendars/date picker;
- new views;
- real-time GTFS-RT/SIRI;
- trams, funicular and non-Euskotren operators;
- any change to the wide output shape.

## Open risks

- GTFS/PDF differences will appear during the first diff; the allowlist process must stay empty by default and reviewed.
- The rolling feed expires; the 7-day staleness gate and daily rebuild are mandatory.
- GTFS stop IDs/names may change; the hard alias check will surface it.
- Night-calendar classification may need tuning against the PDF night calendars.
- The licence has minor portal inconsistencies (general legal link, legacy “do not alter” clause); attribution plus a change notice is the mitigation.
- GTFS contains more data than the current wide table; the first migration deliberately filters it.

## References

- [Evaluate Euskotren GTFS as a timetable source](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/map.md)
- [Feed freshness research](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/research/01-feed-freshness.md)
- [Coverage research](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/research/02-coverage.md)
- [Licence research](research/license.md)
- [GTFS migration map](map.md)
- Resolved tickets: [adapter](issues/01-adapter-boundary.md), [identity/calendars](issues/02-service-identity-calendars.md), [stop aliases](issues/03-stop-aliases.md), [validation](issues/04-validation-pdf-diff.md), [build/rollout](issues/05-build-refresh-rollout.md), [licence](issues/06-license-attribution.md).
