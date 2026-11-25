# Compare GTFS coverage with the current PDF-derived data

Type: research
Status: resolved
Parent: [Evaluate Euskotren GTFS as a timetable source](../map.md)

## Question

How does the GTFS content compare with the current PDF-derived services — routes, trips, stops, calendars, missing or extra services, naming and date-specific behaviour — and what mapping would a GTFS pipeline need?

## Answer

Resolved 2026-11-25.

- The GTFS has 5,165 trips across 13 routes; the current four lines correspond to E1, E3, E3a, E4, L3, T0 and T1 (2,254 rail trips), against 2,225 current services. The order of magnitude matches; E3a accounts for 68 trips not in the current data.
- Stop sets align after normalization: E1 50/50, E3 16/16, T1 23/23, T0 11 (subset of E2-T1's 23), E4 26 vs 25, L3 7 (subset of E3-L3's 16).
- GTFS carries the reported Arroa service and the full Durango–Pasaia pattern.
- GTFS names differ systematically (`Arroa-Zestoa` vs `Arroa (Zestoa)`, `Bentaberri-Donostia` vs `Benta-Berri (Donostia)`); the adapter needs a stop alias map.
- E2-T1 is split into T0 (Añorga–Pasaia) and T1 (Lasarte–Hendaia) in GTFS; E3-L3 is split into E3, L3 and an E3a branch (Lutxana–Sondika) not in the current data.
- GTFS uses date-specific `service_id`s and `calendar_dates` holiday exceptions; the current model uses generic `WD/SA/SU/WE/FN/SN` calendars.
- GTFS has separate arrival/departure times and lists only served stops; the current model uses one time per stop and expands every service to the full stop list.
- GTFS also contains trams, the funicular and FCC; those are outside the current scope.

See [research/02-coverage.md](../research/02-coverage.md).

## Comments

- Charted 2026-11-25 from `gtfs_euskotren.zip` and the current stop registry.
