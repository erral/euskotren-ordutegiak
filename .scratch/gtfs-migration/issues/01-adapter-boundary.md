# Decide the GTFS adapter boundary and Service mapping

Type: grilling
Status: open
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

Where does the GTFS adapter live, and how does it map GTFS rows to the existing `Service` / `StopTime` model?

Cover at least:

- **Adapter boundary**: a new `euskotren_timetable/gtfs.py` (or `parse_gtfs.py`) that returns `list[Service]`, leaving `workbook.py`, `site.py` and `service_order.py` unchanged.
- **Route filtering and line mapping**: E1, E3, E4, L3, T0, T1; merge T0+T1 into E2-T1; merge E3+L3 into E3-L3; exclude E3a and the non-rail routes.
- **Time semantics**: GTFS has separate arrival and departure times; the current `StopTime.time` is a single displayed time. Use the departure time at every served stop, the first departure for `Service.departure`, and the last arrival for `Service.arrival`.
- **Missing/pass/unpublished mapping**: omitted GTFS stops become `not_served`; GTFS has no `?`; use `pickup_type` / `drop_off_type` only where they carry a distinction that matters for the printed timetable.
- **Pattern vocabulary**: keep the current `through` / `short-turn` (and special patterns) rather than importing GTFS trip semantics.
- **Provenance**: keep GTFS `trip_id`, `service_id` and `feed_version` as sidecar metadata, not in the public service ID.

➡️ Recommendation: a thin `gtfs.py` adapter returning `list[Service]`; filter and map routes in a small table; use departure times for display and arrival only for `Service.arrival`; fill omitted stops as `not_served`; keep the current pattern vocabulary; keep GTFS IDs as provenance.

## Comments

- Charted 2026-11-25. Inherits the evaluation decisions on the source of truth and first-migration scope.
