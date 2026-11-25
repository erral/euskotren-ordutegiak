# GTFS coverage versus the current PDF-derived data

Evidence collected 2026-11-25 from `gtfs_euskotren.zip`.

## Feed size and routes

The GTFS has **5,165 trips** across **13 routes** and **812 stop records** (all location types, including entrances and nodes).

Rail routes relevant to the current pipeline:

| GTFS route | Name | Trips | Current line |
|---|---|---:|---|
| E1 | Bilbao–Donostia | 584 | E1 |
| E3 | Lezama–Kukullaga | 331 | E3-L3 |
| E3a | Lutxana–Sondika | 68 | **not currently modelled** |
| E4 | Bilbao–Bermeo | 183 | E4 |
| L3 | Matiko–Kukullaga | 284 | E3-L3 |
| T0 | Añorga–Pasaia | 235 | E2-T1 |
| T1 | Lasarte/Oria–Hendaia | 569 | E2-T1 |

The rail subset is 2,254 GTFS trips, against 2,225 services in our current PDF-derived dataset. The difference includes E3a and GTFS calendar variants; it is the same order of magnitude.

The GTFS also contains trams (TG1, TG2, TR, 41), the Larreineta funicular (FE) and an FCC route. Those must be filtered out for the current scope.

## Stop-set comparison

After normalizing punctuation and municipality suffixes, the stop sets align closely:

| GTFS route | GTFS distinct stops | Current line stops | Observation |
|---|---:|---:|---|
| E1 | 50 | 50 | Same set; names differ in formatting |
| E3 | 16 | 16 | Same set; names differ |
| E3a | 3 | — | Lutxana-Erandio, Zangroiz-Sondika, Sondika; a branch absent from current data |
| T1 | 23 | 23 | Same set; names differ |
| T0 | 11 | 23 | Añorga–Pasaia subset of the current E2-T1 corridor |
| E4 | 26 | 25 | Almost the same set; one extra GTFS station record |
| L3 | 7 | 16 | Subset of E3-L3 |

Stop names differ systematically:

- GTFS: `Arroa-Zestoa`, `Añorga-Donostia`, `Bentaberri-Donostia`, `Zazpikaleak/Casco Viejo-Bilbao`.
- Current: `Arroa (Zestoa)`, `Añorga (Donostia)`, `Benta-Berri (Donostia)`, `Zazpikaleak/Casco Viejo (Bilbao)`.

A GTFS adapter therefore needs a stop alias/mapping layer. The `translations.txt` file provides language translations but does not reproduce our canonical parenthesised names.

## Route and line mapping

- **E2-T1** is one printed corridor in our data, but GTFS splits it into **T0** (Añorga–Pasaia) and **T1** (Lasarte/Oria–Hendaia). The E2-T1 stop set is the T1 set; T0 is a subset. A GTFS adapter must decide whether to merge T0+T1 under the E2-T1 line or expose them separately.
- **E3-L3** is one printed corridor in our data; GTFS has **E3** (Lezama–Kukullaga), **L3** (Matiko–Kukullaga) and **E3a** (Lutxana–Sondika). E3+L3 stop sets are already modelled; E3a is not.
- E1 and E4 map one-to-one.

## Calendar model

- Our model uses generic calendars: `WD`, `SA`, `SU`, `WE`, `FN`, `SN`.
- GTFS has 20 `service_id`s with date ranges plus `calendar_dates` exceptions for specific dates (2026-12-01, 04, 06, 07, 08, 11, 15, 18, 20, 21, 22, 24, 25, 29, 31 and 2027-01-01 in this snapshot).
- GTFS splits ordinary weekdays into Mon–Thu and Friday service_ids in at least one case; the same Arroa trip exists under both.
- GTFS therefore supports **date-specific** output (holiday schedules, Christmas Eve/Day, etc.), which the current generic-calendar site cannot represent directly.
- A GTFS adapter must either:
  - derive generic day-type calendars from GTFS, losing the date exceptions, or
  - extend the model/site to date-specific service selection, gaining the holiday accuracy.

## Time and stop semantics

- GTFS `stop_times` has separate `arrival_time` and `departure_time`; our `StopTime` stores one time per stop. Example: Deba 06:40/06:43 and Zumaia 06:57/07:00 on the Arroa trip.
- GTFS lists only stops served. Our model expands every service to the line's full stop list with `not_served` / `pass` entries. A GTFS adapter would fill the missing stops with `not_served`.
- GTFS includes `pickup_type` / `drop_off_type`; these may matter for conditional stops (e.g., Altzola). Our `pass` and `unpublished` states do not have a direct GTFS equivalent except omission/`pickup_type`.
- GTFS includes shapes, transfers, pathways, levels and fares that the current pipeline does not use.

## Conclusion

GTFS covers the current four lines and the reported Arroa service, and adds E3a and date-specific calendars. The main migration costs are a stop alias map, an E2-T0/T1 and E3/E3a/L3 route mapping, a calendar/date model decision, and a rule for arrival versus departure times.
