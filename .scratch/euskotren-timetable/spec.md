# Euskotren single timetable — implementation spec

- **Status**: implementation-ready
- **Date**: 2026-11-21
- **Map**: [map.md](map.md)
- **Scope**: current winter 2026, lines E1, E2/T1, E3/L3 and E4. Weekdays first, then weekend/holiday calendars, then night calendars.

## 1. Goal

Produce one Excel workbook that consolidates the current winter-2026 Euskotren train timetables from the official PDFs. The workbook has a master service index and one corridor matrix per line and direction, built from a normalized (service, stop, time) dataset. It must be printable to PDF and clean enough to export to CSV, JSON or an API later.

The map ends at this spec and the proven prototype. The production parser and workbook generator are a separate effort.

## 2. Non-goals

- Building the production parser, API or real-time feed in this effort.
- Tram, funicular, bus, museum train and the Lutxana–Sondika shuttle.
- Summer, historical or future seasonal timetables.
- One-off special services such as football extras.
- Fares, accessibility data and stop geo-coordinates.
- Using the official search engine as an oracle. It is only a spot-check.

## 3. Sources and provenance

- Canonical source: the official winter-2026 PDFs linked from `https://euskotren.eus/eu/tren/ordutegiak`.
- The 21 November 2026 updates supersede the 7 September 2026 versions for the affected E1/T1 sections.
- The 2026 network schematic is a cross-check only; it predates the new Donostia stations.
- The official search engine is scriptable but exposes only boarding/alighting times, no trip IDs, a ~31-day horizon and unreliable holidays. Use it only for spot-checks.
- Every run records a manifest: PDF URL, SHA-256, fetch date, page count, season, `valid_from`, open `valid_to` and generator version.
- Supporting artifacts:
  - `research/01-stop-inventory.md`
  - `research/01-stop-headers.json`
  - `research/01-user-corrections.md`
  - `research/02-search-engine-validation.md`
  - `prototypes/e1-weekday-parser/`

## 4. Canonical stop lists

There is **no City entity**. Stops that share a municipality are distinct stations. Keep the published Basque name and add the Spanish alias where the PDF prints one.

### E1 — Pasaia → Matiko-Bilbao (50 stops)

Pasaia, Altza (Donostia), Herrera (Donostia), Intxaurrondo (Donostia), Loiola (Donostia), Anoeta (Donostia), Amara Donostia, Kontxa-Zentroa (Donostia), Benta-Berri (Donostia), Lugaritz (Donostia), Añorga (Donostia), Errekalde (Donostia), Usurbil, Aia-Orio, San Pelaio (Zarautz), Zarautz, Zumaia, Arroa (Zestoa), Deba, Mendaro, Altzola (Elgoibar), Toletxegain (Elgoibar), Elgoibar, Azitain (Eibar), Eibar, Ardantza (Eibar), Amaña (Eibar), Unibertsitatea (Eibar), San Lorentzo (Ermua), Errotabarri (Ermua), Ermua, Zaldibar, Berriz, Traña Abadiño, Durango, Euba (Amorebieta), Amorebieta Geltokia, Lemoa, Bedia, Usansolo, Zuhatzu (Galdakao), Ariz (Basauri), Etxebarri, Kukullaga-Etxebarri, Otxarkoaga (Bilbao), Txurdinaga (Bilbao), Zurbaranbarri (Bilbao), Zazpikaleak/Casco Viejo (Bilbao), Uribarri (Bilbao), Matiko-Bilbao.

- The `Amara → Matiko` subset drops Pasaia, Altza, Herrera, Intxaurrondo, Loiola and Anoeta (44 stops).
- `Altzola` is conditional: 8:56, 12:56, 19:56, 21:56.
- The Pasaia–Amara section is part of the through service and overlaps E2.

### E2/T1 — Hendaia → Lasarte-Oria (23 stops)

Hendaia, Irun Ficoba, Irun, Belaskoenea (Irun), Bentak (Irun), Gaintxurizketa (Lezo), Oiartzun, Fanderia (Errenteria), Errenteria, Galtzaraborda (Errenteria), Pasaia, Altza (Donostia), Herrera (Donostia), Intxaurrondo (Donostia), Loiola (Donostia), Anoeta (Donostia), Amara Donostia, Kontxa-Zentroa (Donostia), Benta-Berri (Donostia), Lugaritz (Donostia), Añorga (Donostia), Errekalde (Donostia), Lasarte-Oria.

- `Gaintxurizketa` is conditional, every 30 minutes.
- The reverse direction is the same sequence reversed.

### E3/L3 — Lezama → Kukullaga-Etxebarri via Matiko (16 stops)

Lezama, Kurtzea (Lezama), Zamudio, Lekunbiz (Zamudio), Derio, Elotxelerri (Loiu), Larrondo (Loiu), Sondika, Ola (Sondika), Matiko-Bilbao, Uribarri (Bilbao), Zazpikaleak/Casco Viejo (Bilbao), Zurbaranbarri (Bilbao), Txurdinaga (Bilbao), Otxarkoaga (Bilbao), Kukullaga-Etxebarri.

- **L3 pattern**: Matiko-Bilbao → Kukullaga-Etxebarri (stops 10–16).
- **E3 pattern**: Lezama → Kukullaga-Etxebarri via Matiko (all 16 stops).
- E3 calls at `Matiko-Bilbao`.

### E4 — Matiko-Bilbao → Bermeo (25 stops)

Matiko-Bilbao, Uribarri (Bilbao), Zazpikaleak/Casco Viejo (Bilbao), Zurbaranbarri (Bilbao), Txurdinaga (Bilbao), Otxarkoaga (Bilbao), Kukullaga-Etxebarri, Etxebarri, Ariz (Basauri), Zuhatzu (Galdakao), Usansolo, Bedia, Lemoa, Amorebieta Geralekua, Zugastieta (Muxika), Muxika, Lurgorri (Gernika), Gernika, Institutua (Gernika), Forua, S. Kristobal (Busturia), Axpe (Busturia), Itsasbegi (Busturia), Mundaka, Bermeo.

- `Amorebieta Geltokia` (E1) and `Amorebieta Geralekua` (E4) are distinct stops on distinct lines.
- The 22:12 train reaches Bermeo on Saturdays and only Gernika on Sundays/holidays.

### Shared trunks

- **E1 ↔ E2**: Pasaia–Errekalde.
- **E1 ↔ E4**: Lemoa–Matiko.
- **E1 ↔ E3/L3 ↔ E4**: Matiko–Kukullaga-Etxebarri.

## 5. Normalized data model

Use a relational or record-based schema with these entities.

### Stop

- `stop_id` — network-wide, `S001`…
- `name_eu` — canonical Basque name.
- `name_es` — Spanish alias where published.
- `notes` — conditional-stop and other stop-level conditions.

### Line and direction

- `line_id` — `E1`, `E2-T1`, `E3-L3`, `E4`.
- `name`, `terminals`.
- `direction_id`, `origin_stop_id`, `destination_stop_id`.
- `line_stop`: `line_id`, `direction_id`, `sequence`, `stop_id`, `branch_id`/null, `marker` (`trunk`, `branch`, `through`).

A line has a **display order** of stops per direction. A service has its own **calling pattern**. They are separate.

### Service

- `service_id` — deterministic: `{line}-{direction}-{calendar}-{departure}`, e.g. `E1-PASAIA-MATIKO-WD-0535`.
- `primary_line_id`.
- `pattern` — semicolon-separated tags: `full`, `short-turn`, `limited-stop`, `through`, `L3`, `E3`.
- `direction_id`.
- `calendar_id`, `valid_from`, `valid_to`.
- `origin_stop_id`, `destination_stop_id`, `departure`, `arrival`.
- `source_pdf`, `frequency_rule_ids`, `notes`.

### Stop time

- `service_id`, `stop_id`, `sequence`, `time`, `day_offset` (0 or +1), `disposition`.
- `disposition`: `stop`, `pass`, `not_served`.
- In the matrix: `stop` → time; `pass`/`not_served` → blank; unpublished → `?`.
- Preserve the source symbol (`>` or `-`) as provenance in the normalized record.

### Calendar

- `calendar_id`, `name`, `day_types`, `valid_from`, `valid_to`, `notes`.
- Every service belongs to exactly one calendar.

### Frequency rule

- `rule_id`, `source_text`, `source_pdf`, `page`, `block`.
- `origin_stop_id`, `start_time`, `end_time`, `interval_minutes`.
- `calendar_id`, `expanded_service_ids`, `notes`.

### Membership and manifest

- `service_sheet`: `service_id`, `sheet_name` — one row per corridor where the service appears.
- `manifest`: PDF URL, SHA-256, fetch date, page count, season, `valid_from`, `valid_to`, generator version.
- `corrections`: sidecar keyed by `service_id`/`stop_id`.

## 6. Extraction pipeline

### 6.1 Acquire and diff

1. Fetch the timetable page.
2. Extract PDF links and compare against the manifest checksums.
3. Report new, changed and removed PDFs before parsing.

### 6.2 Parse one PDF page

1. Identify line, direction, page and day-type blocks.
2. Extract header words and coordinates with `pdftotext -bbox-layout` or an equivalent.
3. Reconcile header names against the canonical stop list.
4. Build the column grid from the header or a complete row.
5. Cluster row words by y and map cells to columns by x.
6. Read times, `>` (pass) and `-` (not served).

### 6.3 Merge full-line and partial tables

1. Parse the full-line table.
2. Parse the partial table for the guaranteed-stop section.
3. Match services by their time at the section boundary.
4. Merge the partial times into the full-line row.
5. If there is no match, leave the intermediate stops as `?`; never guess.

### 6.4 Footnotes

- Bracket-match a footnote time between the adjacent stops; require exactly one match.
- Flag zero or multiple matches.
- Conditional stops become real columns; times only on the services that call.
- Frequency notes expand (6.5).
- Destination variants split (6.7).
- Train-change and operational notes go to `Notes`.
- One-off specials are out of scope.

### 6.5 Frequency expansion

- In a frequency note, `>` is a range separator.
- Parse `start > end`, interval (`1 h`, `30 min`, `15 min`, …), optional origin prefix, multiple clauses.
- Generate `start + n × interval`, inclusive of the end.
- Merge with explicit rows; explicit rows win; deduplicate by departure time.
- Clauses with different origins generate separate sets; if their shared-stop times match, merge into one service row and retain both rule IDs.
- Stop-frequency notes never generate services.
- Support ranges crossing midnight with a day offset.
- Validate by count, first/last time and comparison with explicit rows.

### 6.6 Calendars

- One calendar per service; preserve the source grouping.
- Day types: weekday, Saturday, Sunday, holiday, Friday night/holiday eve, Saturday night.
- After-midnight times belong to the service day that started the previous evening.
- Holiday dates are deferred; phase one uses the calendar label.
- Split calendar-dependent destinations into one service per calendar.

### 6.7 Cross-line membership

- A service appears in every line/direction sheet where it calls at two or more consecutive stops in that sheet's travel direction.
- A single shared terminus is not enough.
- The `Master` records `Appears in`; the corridor sheet repeats the service ID.
- Partial rows are normal.

## 7. Workbook contract

### File and language

- `euskotren_timetables_winter_2026_v1.xlsx`.
- Basque-primary content with Spanish aliases and notes.
- Sheet names use line code plus terminals.

### Sheets

1. `README`
2. `Stops`
3. `Calendars`
4. `Manifest`
5. `Master`
6. `E1 Pasaia-Matiko`
7. `E1 Matiko-Pasaia`
8. `E2-T1 Hendaia-Lasarte`
9. `E2-T1 Lasarte-Hendaia`
10. `E3-L3 Lezama-Kukullaga`
11. `E3-L3 Kukullaga-Lezama`
12. `E4 Matiko-Bermeo`
13. `E4 Bermeo-Matiko`
14. `Frequency rules`
15. `Validation`

### Corridor sheet layout

- Stops as columns in travel order; branch and through stops inline.
- Header block per stop: `Stop ID`, `Basque name`, `Spanish alias`, `Branch/through marker`.
- Service metadata columns: `Service ID`, `Primary line`, `Pattern`, `Calendar`, `Valid from`, `Valid to`, `Origin`, `Destination`, `Departure`, `Arrival`, `Notes`.
- One row per service; times in stop cells.
- Calendar blocks stacked: Weekday, Saturday, Sunday + holiday, Night, each with a section header.
- `Calendar` column repeats the calendar ID for filtering.

### Master index

- One row per service: `Service ID`, `Primary line`, `Pattern`, `Appears in`, `Direction`, `Calendar`, `Valid from`, `Valid to`, `Origin`, `Destination`, `Departure`, `Arrival`, `Source PDF`, `Frequency rule(s)`, `Notes`.

### Time and blank conventions

- 24-hour `HH:MM`.
- After-midnight `24:xx`/`25:xx`; `day_offset` in machine-readable exports.
- Blank = does not stop; `?` = time not published; no `>`/`-` in cells.
- Conditional stops show their time only where they apply.

### Print and readability

- Freeze metadata columns and header rows.
- Repeat headers on every printed page.
- Landscape, fit to width, per-line colour, autofilter.
- Rotate stop headers 90°; narrow columns; `Stops` carries full names and aliases.
- Conditional formatting for conditional stops and notes.

### Provenance

- `README`: sources, checksums, season, validity, generation date, generator version.
- `Manifest`: source PDF, checksum, fetch date, page count.
- `Frequency rules`: rule text, source, expanded service IDs.
- `Stops`: stop-level notes.
- `Master`: source PDF and frequency rule(s) per service.
- The workbook is generated output; corrections live in the sidecar.

## 8. Calendar and versioning model

- Calendars are named service sets: Weekday, Saturday, Sunday + holiday, Saturday + Sunday + holiday, Friday night/holiday eve, Saturday night.
- Every service belongs to exactly one calendar.
- Preserve the source grouping; split Saturday/Sunday only where the PDFs split.
- Service day: a 00:30 Sunday service belongs to Saturday night.
- Holiday eves are first-class; holiday dates are deferred.
- Each timetable version carries `valid_from`, open `valid_to`, season and source PDF.
- The generator uses the latest valid PDF per line/direction as of the generation date; older versions are archived, not merged.

## 9. Validation

### Layers

1. **Structural**: monotonic times, stop order, no stray symbols, stops exist in `Stops`, every service has a calendar and pattern, `?` only in the expected set, every `Appears in` corridor has two consecutive stops, every service has at least two stops.
2. **Source**: service counts, first/last service, conditional stops, visual matrix diff against the PDF.
3. **Cross-direction/calendar**: counts and first/last per direction and calendar, `day_offset`, destination variants.
4. **Search-engine spot-check**: 1–3 terminus-to-terminus services per line/day type within 31 days; departure/arrival only; never an oracle.

### Manual and automated

- Structural, source and cross checks run automatically into `Validation` and a Markdown report.
- A human reviews every line/direction/calendar sheet at least once and spot-checks 3–5 services per sheet.
- Sign-off per sheet; unresolved failures block sign-off.

### Tolerances and regression

- Exact service counts and first/last times.
- The `?` count must match the expected unpublished set; a new `?` is a failure until reviewed.
- Rerun on every regeneration and compare against the baseline; new `?`, count changes, first/last changes or conditional-stop changes fail until reviewed.

## 10. Refresh and versioning

- Manifest of PDF URLs and SHA-256 checksums; diff before parsing.
- Sidecar corrections (YAML/CSV) keyed by service ID/stop, applied after parsing.
- The workbook is never hand-edited.
- Fetch, checksum, parse, validate and render are automated; review and sign-off are human.
- Each refresh produces a change report: new/removed/changed services, new `?`, count changes.
- On-demand refresh; no scheduler.

## 11. Phased delivery

### Phase 0 — foundation

- Manifest and checksum diff.
- Canonical stop lists and `Stops` sheet.
- Normalized schema.
- Workbook skeleton and `README`.
- Sidecar corrections format.

### Phase 1 — weekdays

- E1 Pasaia → Matiko and Matiko → Pasaia, including the Amara subset.
- E2/T1 both directions.
- E3/L3 both directions.
- E4 both directions.
- Full-line/partial-table merge, footnote rules, frequency expansion, cross-line membership.
- Validate and sign off each sheet.

### Phase 2 — weekend and holiday

- Saturday.
- Sunday + holiday.
- Combined Saturday + Sunday + holiday where the source merges them.
- Validate and sign off.

### Phase 3 — night

- Friday night / holiday eve.
- Saturday night.
- `day_offset` and `24:xx`/`25:xx`.
- Validate and sign off.

Each phase follows: extract → merge → normalize → validate → render → human sign-off.

## 12. Acceptance criteria

- Every in-scope line, direction and calendar is present.
- Stop lists match the inventory.
- Every service has a calendar, `valid_from`, `valid_to`, origin, destination and pattern.
- No `>` or `-` in the matrix; `?` only where expected.
- Service counts and first/last times match the PDFs exactly.
- Structural, source and cross checks pass.
- Human sign-off per sheet.
- `Master`, `Stops`, `Calendars`, `Manifest`, `Frequency rules`, `Validation` are complete.
- Workbook opens, prints, filters and reads correctly.
- Sidecar corrections are applied.
- `Appears in` membership matches the shared-trunk rules.

## 13. Open items and risks

- **Unpublished intermediate times**: partial tables cover only some services; `?` is the explicit marker. A future source may fill them.
- **E4 22:12 destination variant**: split by calendar; confirm the Saturday/Sunday rows in the source.
- **E3/L3 patterns**: L3 and E3 share a sheet; ensure the `Pattern` split is correct.
- **Amorebieta Geltokia vs Geralekua**: distinct stops; do not merge them.
- **Conditional stops**: Altzola, Gaintxurizketa and Ola must stay sparse, not blank.
- **Holiday dates**: deferred; phase one uses calendar labels.
- **Special services**: one-off extras remain out of scope.
- **Search engine**: spot-check only.
- **PDF layout changes**: manifest and validation catch them; the parser may need adjustment each season.
- **Excel limits**: sheet names cannot contain `/`, so `E2-T1` and `E3-L3`.

## 14. Production build backlog (separate effort)

1. PDF manifest and checksum diff.
2. Coordinate-based PDF parser and column mapper.
3. Full-line/partial-table merger.
4. Footnote and frequency expansion engine.
5. Normalized store and schema.
6. Workbook renderer with corridor sheets and master index.
7. Validation harness and baseline comparison.
8. Sidecar correction loader.
9. Change report generator.
10. Refresh CLI.

## 15. References

- [Map](map.md)
- [Stop inventory](research/01-stop-inventory.md)
- [Stop headers JSON](research/01-stop-headers.json)
- [User corrections](research/01-user-corrections.md)
- [Search-engine research](research/02-search-engine-validation.md)
- [E1 weekday prototype](prototypes/e1-weekday-parser/README.md)
- [Glossary](../../GLOSSARY.md)
