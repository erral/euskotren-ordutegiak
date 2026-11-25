# Migrate the static timetable pipeline to Euskotren GTFS

Status: route clear — parallel PDF + GTFS publication and comparator implemented on `feat/gtfs-migration`.

## Destination

A decision-complete implementation specification for replacing the PDF static pipeline with Euskotren GTFS, preserving the current four lines, workbook and wide HTML outputs. Implementation is a separate effort.

## Notes

- **Effort type**: planning. This map produces a specification; it does not implement the GTFS adapter.
- **Prior evaluation**: [Evaluate Euskotren GTFS as a timetable source](https://github.com/erral/euskotren-ordutegiak/blob/research/gtfs-evaluation/.scratch/gtfs-evaluation/map.md) on branch `research/gtfs-evaluation` (commit `36af425`). Inherited constraints:
  1. GTFS is the static source of truth; the PDFs are a validation/provenance and reference build.
  2. Keep the current four lines (E1, E2-T1, E4, E3-L3); merge GTFS T0+T1 under E2-T1; defer E3a; trams, funicular and FCC stay out.
  3. Derive the current `WD/SA/SU/WE/FN/SN` calendars first; retain date-specific GTFS data for a later date-aware view.
  4. Keep the current workbook and wide HTML timetable; add no new user-facing views.
  5. Refresh from GTFS daily with a staleness alarm; never publish a stale feed window.
- **Current pipeline**: `euskotren_timetable/parse_*.py` → `Service` / `StopTime` → `workbook.py` and `site.py`; PDF manifest and GitHub workflow.
- **GTFS source**: `https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip`; discovered from the Moveuskadi `data-index.json`; `feed_start_date`/`feed_end_date` are a rolling window (2026-11-25 → 2026-12-30 at the evaluation date).
- **Glossary**: [GLOSSARY.md](../../GLOSSARY.md), especially Service, Stop, Stop disposition, Stop time, Line, Direction, Corridor, Calendar, Service day and Service order.
- **Branch**: `wayfinder/gtfs-migration`; planning branch, no PR yet.
- **Evidence date**: 2026-11-25.

## Decisions so far

- [Decide the GTFS adapter boundary and Service mapping](issues/01-adapter-boundary.md): thin in-package `gtfs.py` adapter using stdlib `zipfile`/`csv`; explicit route mapping (T0+T1 → E2-T1, E3+L3 → E3-L3, E3a excluded); departure times for display; omitted stops as `not_served`; GTFS IDs kept as sidecar provenance.
- [Decide service identity and calendar derivation](issues/02-service-identity-calendars.md): preserve the public `<line>-<direction>-<calendar>-<departure>` IDs; deduplicate to one service per line/direction/calendar/departure; derive the existing per-line calendars from representative feed dates; ignore holiday exceptions for the first migration; keep the current ordering contract.
- [Decide stop alias and canonical-name mapping](issues/03-stop-aliases.md): map GTFS parent stations to the existing canonical stops via a reviewed, ID-keyed alias table; keep the canonical names and display order; fail the build on unmapped in-scope stops; exclude E3a.
- [Decide validation and the PDF-diff contract](issues/04-validation-pdf-diff.md): hard release gate against the pinned PDF-derived build; exact stop-time and `not_served` comparison; versioned allowlist starting empty; CI diff report; golden Arroa/E1/E2/E3/E4/night examples; holiday exceptions excluded from the first comparison.
- [Decide build, refresh and rollout](issues/05-build-refresh-rollout.md): `--source gtfs|pdf` with a staged default; generated GTFS manifest and feed metadata; daily scheduled build with a 7-day staleness floor and hard PDF diff; one-week `/` PDF vs `/gtfs/` GTFS parallel publication with both workbooks, then GTFS at `/`; CC BY 4.0 attribution at cutover.
- [Confirm Open Data Euskadi licence and attribution](issues/06-license-attribution.md): the dataset is CC BY 4.0; attribute Eusko Trenbideak, link the source and licence, note changes and the feed version; derived outputs may be published under CC BY 4.0 with the code under GPL-2.0.
- [Write the GTFS migration specification](issues/07-write-spec.md): spec written at [`spec.md`](spec.md); adapter, mapping, calendars, stop aliases, validation, build/refresh, parallel publication, licence/attribution, testing and implementation boundary defined.
- [Decide GTFS-to-published calendar reconciliation](issues/08-calendar-reconciliation.md): parallel publication, not reconciliation; `/` stays PDF, `/gtfs/` is GTFS, `/compare.html` is the side-by-side comparator; collision suffixes; representative-day calendars; integrity gate.

## Not yet specified

None. Date-aware calendars, E3a and real-time remain deferred follow-ups.

## Out of scope

- Implementing the GTFS adapter or changing the workbook/site generator; the destination is the specification.
- E3a, date-specific calendars/date picker and new user-facing views.
- Real-time integration (GTFS-RT/SIRI).
- Trams, the funicular and non-Euskotren operators.
- Changing the wide workbook/HTML output shape.
- Resolving SIRI/NeTEx access; the evaluation recorded it as unavailable.
