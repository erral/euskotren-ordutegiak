# Evaluate Euskotren GTFS as a timetable source

Status: charted 2026-11-25. Source-of-truth decision accepted; calendar/route/output decision open.

## Destination

A written evaluation and recommendation on whether the timetable pipeline should adopt Euskotren GTFS as its static source of truth, keep the PDFs, or run both — with evidence on freshness, coverage, feed access and migration cost. Implementation is a separate effort.

## Notes

- **Effort type**: planning/research. The map resolves the source-of-truth decision; it does not build a GTFS parser.
- **Issue tracker**: local markdown. This file is the map; tickets live in `issues/`. See `docs/agents/issue-tracker.md`.
- **Branch**: `research/gtfs-evaluation`; a research branch, not a merge candidate.
- **Data index**: `https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/data-index.json`; the `.data.Euskotren` key lists the feeds.
- **Current pipeline**: six PDF posters fetched 2026-11-21; parsers in `euskotren_timetable/parse_*.py`; `Service` / `StopTime` model; workbook and static HTML.
- **Glossary**: [GLOSSARY.md](../../GLOSSARY.md), especially Service, Stop, Calendar, Service day and Timetable version.
- **Evidence date**: 2026-11-25.

### Standing decisions (settled during charting)

1. The destination is an **evaluation/recommendation**, not a GTFS implementation.
2. The comparison covers the current four rail lines (E1, E2-T1, E4, E3-L3), not trams or the funicular.
3. Real-time feeds are evaluated for relevance but are not adopted in the static pipeline.
4. Research evidence lives in `research/` and on this branch; no PR is opened.

## Decisions so far

- [Verify Euskotren feed freshness and access](issues/01-feed-freshness.md): static GTFS is refreshed daily and already contains the Arroa 06:53 service; GTFS-RT trip updates are live, while alerts/vehicle positions are empty and SIRI/NeTEx return a logout page.
- [Compare GTFS coverage with the current PDF-derived data](issues/02-coverage.md): stop sets align after name normalization; E2-T1 splits into T0+T1 in GTFS, E3a is an extra branch, and GTFS carries date-specific holiday exceptions.
- [Assess GTFS licensing, URL stability and operating constraints](issues/03-license-operations.md): URLs are stable and the feed is refreshed daily, but the feed window is short, the licence/attribution terms need confirmation, and SIRI/NeTEx access is blocked.
- [Decide the timetable source of truth and refresh policy](issues/04-source-of-truth.md): GTFS is the static source of truth; PDFs remain a validation/provenance and reference build; rebuild daily and never publish a stale GTFS window.

## Not yet specified

- Migration architecture: a GTFS adapter feeding the existing `Service` model, a direct GTFS-to-workbook/HTML path, or a parallel validation path.
- Whether GTFS-RT trip updates become a later live-service feature.
- Whether the Open Data Euskadi licence permits the intended redistribution, and what attribution the workbook/site must carry.

## Out of scope

- Implementing the GTFS parser or changing the workbook/site generator; the destination is the evaluation.
- Real-time integration (GTFS-RT/SIRI) in the static timetable.
- Trams, the funicular and non-Euskotren operators.
- Replacing the Excel workbook or republishing the GTFS feed.
- Resolving the SIRI/NeTEx access block; it is recorded as a finding and a risk.
