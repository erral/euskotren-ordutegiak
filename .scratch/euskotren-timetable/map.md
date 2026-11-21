# Euskotren single timetable

**Status**: route clear — implementation spec written 2026-11-21.

## Destination

An implementation-ready spec and a proven parsing approach for one Excel workbook that consolidates the current winter-2026 Euskotren train timetables (E1, E2/T1, E3+L3, E4) from the official PDFs. The workbook holds a master table plus per-line, per-direction tables: columns are stops in travel order (branch stops inline at their junction), rows are services, cells are 24-hour stop times. Delivery order is weekdays, then weekend/holiday calendars, then night calendars; Saturday and Sunday are split only where the source PDFs split them.

Reaching the destination means the spec is written and the extraction approach has been proven on one real PDF; building the production parser is a separate effort.

## Notes

- **Effort type**: planning. The map resolves decisions; it does not build the production pipeline.
- **Issue tracker**: local markdown. This file is the map; tickets live in `issues/`, research in `research/`, prototypes in `prototypes/`. See `docs/agents/issue-tracker.md`.
- **Source**: official PDFs at https://euskotren.eus/eu/tren/ordutegiak, current winter 2026. PDFs are the canonical source; no OCR.
- **Skills**: `research` for PDF and web facts, `prototype` for the extraction proof, `grilling` and `domain-modeling` for the open decisions.
- **Glossary**: [GLOSSARY.md](../../GLOSSARY.md).

### Standing decisions

1. Destination is a spec plus a prototype; the full build is a separate effort.
2. In scope: E1, E2/T1, E3+L3, E4. Lutxana–Sondika is excluded.
3. PDFs are canonical; the official search engine is not required as a source.
4. Output is a master service index plus per-line, per-direction corridor matrices, generated from a normalized (service, stop, time) intermediate. A service appears in every corridor it traverses, with partial rows where it leaves the line.
5. Only the current winter 2026 timetable; day types are modelled, holidays are separate.
6. Branches appear inline at their junction. One table per direction, so every row reads in travel order.
7. Blank cell means "does not stop"; `?` means "time not published". Times are 24-hour; after-midnight services use `24:xx`/`25:xx`.
8. Footnote-only stops (e.g. Altzola) become real columns, with their times placed in the corresponding service rows.
9. Basque published name is canonical, with a Spanish alias and a stable stop ID. There is no City entity: stops that share a municipality are distinct (Eibar-Azitain, Eibar-Ardantza and Eibar are three stops).

## Decisions so far

- [Settle the domain model for lines, branches and services](issues/04-domain-model.md): Service is canonical; no City entity (Eibar-Azitain, Eibar-Ardantza and Eibar are distinct stops); display order is separate from calling pattern; frequency rules expand to explicit services; blank means "does not stop"; Saturday-night services are a distinct day type.
- [Define the calendar and day-type model](issues/07-calendar-model.md): named calendars (each service in exactly one); preserve source grouping; service day with after-midnight offsets; holiday eves first-class; holiday dates deferred; split calendar-dependent destinations; versioned by valid_from/valid_to and source PDF.
- [Reverse-engineer the official timetable search engine](issues/02-search-engine-validation.md): scriptable via a plain GET to `/eu/horarios/resultados` once stop IDs are known, but it exposes only boarding/alighting times, no trip IDs, a ~31-day horizon and unreliable holiday results — use it only as a spot-check, never as an oracle.
- [Prototype: parse one E1 weekday direction into stop-time records](issues/03-prototype-e1-weekday.md): coordinate-based parse of the current 21 Nov PDF works; merged full-line and Pasaia → Zumaia tables; the 05:35 through service is complete across 50 stops; `Traña Abadiño` is one stop; E1 Pasaia → Matiko is a through service; partial tables cover only some services.
- [Inventory stops and canonical column order across in-scope PDFs](issues/01-stop-inventory.md): E1 has a 50-stop through service (44-stop Amara subset), E2/T1 has 23 stops, E3/L3 has 16, E4 has 25; `Amorebieta Geltokia` and `Amorebieta Geralekua` are distinct stops on E1/E4; E3 calls at `Matiko-Bilbao`; shared trunks are mapped.
- [Define the Excel workbook contract](issues/05-workbook-contract.md): Basque-primary workbook with a master service index and eight corridor sheets; a service appears in every line/direction sheet it traverses; shared trunks are E1↔E2 Pasaia–Errekalde, E1↔E4 Lemoa–Matiko, and E1↔E3/L3↔E4 Matiko–Kukullaga; partial rows are normal; deterministic service IDs and network-wide stop IDs.
- [Generalize the footnote, branch and limited-stop extraction rules](issues/06-footnote-branch-rules.md): footnote times are bracket-matched; `?` means "time not published" and blank means "no stop"; a `Pattern` field distinguishes full, short-turn, limited-stop, through, L3 and E3; conditional stops are real columns; through services appear in every corridor; calendar-dependent destinations split with calendar-specific IDs.
- [Define how extracted timetables are validated](issues/09-validation-strategy.md): four validation layers (structural, source, cross-direction/calendar, search-engine spot-check); exact counts and first/last times; a `?` whitelist; a `Validation` sheet plus Markdown report; human sign-off per sheet; regression against the previous baseline on every regeneration.
- [Define the refresh and versioning workflow](issues/10-refresh-workflow.md): manifest plus SHA-256 change detection; sidecar corrections applied on every regeneration; `Manifest` and `README` provenance; the latest valid PDF per line wins mid-season; on-demand refresh with a change report and baseline validation.
- [Define the frequency-rule expansion rules](issues/11-frequency-expansion-rules.md): frequency notes use `>` as a range separator; expand start + n × interval inclusively; explicit rows win and dedupe; clauses with matching shared-stop times merge into one service row; stop-frequency notes never generate services; rule provenance and validation.
- [Write the implementation spec](issues/08-implementation-spec.md): the implementation spec is written at `spec.md`; it assembles the stop lists, data model, extraction pipeline, workbook contract, validation, refresh and phased delivery.

## Not yet specified

<!-- none: the route to the destination is clear -->

## Out of scope

- Lutxana–Sondika shuttle.
- Tram, funicular, bus and museum train services.
- Summer and historical timetables.
- Real-time data, live departures and disruption alerts.
- One-off special services (e.g. football extras).
- The production parser and API build; this effort ends at the spec and prototype.
- Fares, accessibility data and stop geo-coordinates.
- CSV, JSON or API publication beyond the Excel deliverable; a future effort.
- Holiday date list for date-specific views; phase one uses calendar labels only.
