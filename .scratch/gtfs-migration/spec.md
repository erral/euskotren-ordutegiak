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
- the integrity gate and the PDF/GTFS comparator contract;
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

## Integrity gate and comparator

The PDF and GTFS feeds are different timetable editions; the migration does **not** attempt to reconcile them.

The GTFS build must pass a hard **integrity** gate:

- every in-scope GTFS parent station maps exactly once to a canonical stop;
- every in-scope trip maps to a line, direction and canonical stop order;
- no duplicate public service IDs after collision suffixes;
- the feed is present and at least seven days of its validity window remain;
- every service has at least two served stops and a canonical stop set.

The PDF site remains the reference publication at `/`; the GTFS site is published independently at `/gtfs/`. `/compare.html` is the human review mechanism:

- it loads both `services.json` files;
- it filters by line, direction and calendar;
- it renders the PDF and GTFS tables side by side;
- it reports service/departure counts, PDF-only departures, GTFS-only departures and changed departures;
- it links every service to its page in the corresponding site.

The comparator note states that the editions differ and that differences are expected. There is no blocking PDF-equality gate and no allowlist; differences are visible, not suppressed.

## Build and manifest

- CLI: `build-html --source gtfs|pdf --gtfs <zip>`; `pdf` remains the default at `/`, `gtfs` builds the parallel `/gtfs/` site.
- The GTFS path builds the same workbook and site from `load_gtfs_services`; the PDF path remains the reference build.
- Generate `data/gtfs-manifest.json` inside each GTFS site's `data/` directory with the feed metadata and SHA-256.
- Add an optional `gtfs` object to `data/services.json` meta with the feed version/window/source/checksum.
- Carry the feed version/window/licence into the site footer and workbook metadata.
- Do not commit a new manifest daily; the deployed artifact is the record. Keep a committed schema/example.
- Keep the PDF manifest and PDF download path.
- The Frequency rules sheet remains but has no GTFS rules; GTFS trips are explicit.
- The Master `Source PDF` column becomes `Source` and shows the GTFS source/feed identifier.

## Workflow, parallel publication and rollout

### Daily workflow

- Extend `.github/workflows/tests.yml` with a daily schedule after the feed's ~07:00 local publication (for example 06:30 UTC).
- Download the GTFS zip and the pinned PDFs.
- Run the tests, including the GTFS adapter integrity tests.
- Build the PDF site at `/` and the GTFS site at `/gtfs/`; both are linked by the shared banner and the comparator.
- Build both workbooks: `…_pdf.xlsx` and `…_gtfs.xlsx`.
- Validate the composed site and publish it on success; a failed run leaves the last successful deployment live.
- Keep the push/PR/manual test job.

### Publication model

- `/` is the PDF-derived site.
- `/gtfs/` is the GTFS-derived site.
- `/compare.html` is the side-by-side comparator.
- Both workbooks are public.
- This is a permanent parallel publication, not a one-week soak and not a cutover.
- The PDF site is not retired; the GTFS site is an additional, independently sourced view.
- The comparator explicitly states that the two editions are not reconciled.

### Attribution

Add the CC BY 4.0 attribution to the GTFS site footer, the GTFS workbook metadata and the README: credit Eusko Trenbideak, link the GTFS source and the CC BY 4.0 licence, note that the data was transformed, and include the feed version/last-update date.

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

The integrity gate is hard; the comparator is the review surface, not a local convenience check.

## Implementation boundary

In the first migration:

- four lines: E1, E2-T1 (T0+T1), E4, E3-L3 (E3+L3);
- current per-line calendar sets;
- current workbook and wide HTML shapes;
- daily GTFS refresh with a 7-day staleness floor;
- permanent `/` PDF + `/gtfs/` GTFS parallel publication plus the `/compare.html` comparator;
- CC BY 4.0 attribution.

Deferred:

- E3a Lutxana–Sondika;
- date-specific calendars/date picker;
- new views;
- real-time GTFS-RT/SIRI;
- trams, funicular and non-Euskotren operators;
- any change to the wide output shape.

## Open risks

- GTFS/PDF differences are expected; they are surfaced in the comparator and are not suppressed or reconciled.
- The rolling feed expires; the 7-day staleness gate and daily rebuild are mandatory.
- GTFS stop IDs/names may change; the hard alias check will surface it.
- Night-calendar classification may need tuning against the PDF night calendars.
- The licence has minor portal inconsistencies (general legal link, legacy “do not alter” clause); attribution plus a change notice is the mitigation.
- GTFS contains more data than the current wide table; the first migration deliberately filters it.

## Implementation finding (2026-11-25)

The first adapter spike (on `feat/gtfs-migration`) showed that the live GTFS feed and the current PDF output are different timetable editions and calendar groupings:

- **2,186** in-scope GTFS rail trips (E3a excluded) against **2,225** PDF service rows — 39 fewer.
- **913** unique GTFS timetable patterns against **1,521** unique PDF patterns — 608 fewer.
- The date-derived calendar expansion produced 2,845 *calendar candidates*; that is calendar duplication, not more physical services.
- Only 599 unique patterns are common; 922 PDF patterns have no GTFS match and 314 GTFS patterns have no PDF match.
- Seven public-ID conflicts share the same line/direction/calendar/departure but differ in pattern or destination.
- The E1 weekend GTFS trips omit Arroa, while the PDF weekend table publishes it at 08:33.
- The PDF calendars are source-table groups, not pure day types.

Consequence: the **hard PDF equality gate** is not workable, and the date-derived calendar grouping is not reconciled with the PDFs. The chosen implementation is a permanent parallel publication: PDF at `/`, GTFS at `/gtfs/`, and `/compare.html` as the side-by-side review surface. The adapter, the 82-stop alias table, the provenance fields, the GTFS build and the comparator are implemented on `feat/gtfs-migration`.

## References

- [Evaluate Euskotren GTFS as a timetable source](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/map.md)
- [Feed freshness research](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/research/01-feed-freshness.md)
- [Coverage research](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/research/02-coverage.md)
- [Licence research](research/license.md)
- [GTFS migration map](map.md)
- Resolved tickets: [adapter](issues/01-adapter-boundary.md), [identity/calendars](issues/02-service-identity-calendars.md), [stop aliases](issues/03-stop-aliases.md), [validation](issues/04-validation-pdf-diff.md), [build/rollout](issues/05-build-refresh-rollout.md), [licence](issues/06-license-attribution.md).
