# Migrate the static timetable pipeline to Euskotren GTFS

Status: charted 2026-11-25. Adapter mapping decided; service identity/calendars and stop aliases open.

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

## Not yet specified

None beyond the live tickets. The specification ticket consolidates the answers; any remaining implementation detail should be added there rather than kept as fog.

## Out of scope

- Implementing the GTFS adapter or changing the workbook/site generator; the destination is the specification.
- E3a, date-specific calendars/date picker and new user-facing views.
- Real-time integration (GTFS-RT/SIRI).
- Trams, the funicular and non-Euskotren operators.
- Changing the wide workbook/HTML output shape.
- Resolving SIRI/NeTEx access; the evaluation recorded it as unavailable.
