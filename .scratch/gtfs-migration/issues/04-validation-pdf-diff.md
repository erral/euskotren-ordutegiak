# Decide validation and the PDF-diff contract

Type: grilling
Status: open
Blocked by: 01, 02, 03
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

How do we prove the GTFS pipeline matches the current PDF-derived output before cutover?

Cover at least:

- **Dual run**: build both sources in CI and compare the overlapping calendars.
- **Fail conditions**: missing or extra services, stop-time differences, stop-mapping gaps and duplicate IDs.
- **Allowlist**: an explicit list of documented differences; no silent tolerance.
- **Diff report**: a human-readable report of added, removed and changed services.
- **Golden examples**: the Arroa 06:53 service, the E1 05:35 service, representative E2, E3, E4 services and the night calendars.
- **Time comparison**: compare displayed departure times and the `not_served` sets; ignore date-specific `calendar_dates` exceptions for the first migration and record that limitation.
- **Gate**: decide whether the PDF diff is a hard release gate or advisory.

➡️ Recommendation: a hard release gate with an explicit allowlist and a diff report; compare departure times and `not_served` sets exactly for overlapping services; use golden examples across all four lines and the night calendars.

## Comments

- Charted 2026-11-25.
