# Decide service identity and calendar derivation

Type: grilling
Status: open
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

How should GTFS trips become the project's services, IDs and `WD/SA/SU/WE/FN/SN` calendars?

Cover at least:

- **Service IDs**: preserve the current human-readable scheme (`<line>-<direction>-<calendar>-<departure>`) or adopt GTFS `trip_id`s. The current IDs are used by HTML anchors, workbook references and tests; GTFS `trip_id`s are opaque and change with the feed.
- **Deduplication**: GTFS may expose the same physical service under several `service_id`s (for example Mon–Thu and Friday) and may contain duplicate times. Pick one representative per line/direction/calendar/departure.
- **Calendar derivation**: choose representative dates inside the feed window for each of `WD`, `SA`, `SU`, `WE`, `FN` and `SN`; derive services from the trips active on those dates; ignore `calendar_dates` exceptions for the first migration.
- **Ordering**: keep `service_order` and the existing corridor keys.
- **Stability**: current IDs are time-dependent and change when times change; GTFS trip IDs are feed-version-specific. Do not promise cross-feed stability.

➡️ Recommendation: preserve the current human-readable ID scheme; keep the GTFS `trip_id`/`service_id` as provenance; deduplicate to one service per line/direction/calendar/departure; derive calendars from representative dates; ignore holiday exceptions for the first migration; keep the existing sort contract.

## Comments

- Charted 2026-11-25.
