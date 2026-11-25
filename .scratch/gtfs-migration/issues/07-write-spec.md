# Write the GTFS migration specification

Type: task
Status: resolved
Blocked by: 01, 02, 03, 04, 05, 06
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

Produce the destination artifact: `.scratch/gtfs-migration/spec.md`, the decision-complete specification for replacing the PDF static pipeline with Euskotren GTFS.

It must cover:

- the GTFS adapter boundary and the `Service` / `StopTime` mapping;
- route/line filtering and the T0+T1 → E2-T1 mapping;
- service identity, deduplication and `WD/SA/SU/WE/FN/SN` calendar derivation;
- the GTFS → canonical stop alias table;
- validation and the PDF-diff contract, including the allowlist and golden examples;
- build, manifest, refresh cadence, staleness gate and rollout;
- licence/attribution requirements;
- the explicit implementation boundary: what is in the first migration and what is deferred (E3a, date-specific calendars/date picker, new views, real-time).

## Answer

Resolved 2026-11-25. The specification is written at [spec.md](../spec.md).

It covers the GTFS source contract, adapter boundary, route/direction mapping, `Service`/`StopTime` mapping, public service identity and deduplication, per-line calendar derivation, stop aliases, the hard PDF-diff contract, build/manifest, daily workflow, the one-week `/` vs `/gtfs/` parallel publication, CC BY 4.0 attribution, testing, the implementation boundary and open risks.

## Comments

- Charted 2026-11-25.
- 2026-11-25: all decision blockers (01–06) resolved; this task is now on the frontier.
- 2026-11-25: claimed and resolved. The specification is written.
