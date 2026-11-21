# Define the Excel workbook contract

Type: grilling
Status: resolved
Blocked by: 01, 04

## Question

Specify the workbook the parser must emit:

- sheet names and order (master plus per-line, per-direction), including how the multi-brand E2/T1 and E3/L3 PDFs are presented: separate sheets, merged, or one sheet per brand;
- the order of lines in the master table (E1, E2/T1, E3/L3, E4 and their shared trunks);
- how calendars are presented: separate blocks, separate sheets, or a calendar column;
- the header block: stop ID, Basque name, Spanish alias, branch marker;
- one row per service, with origin, destination, direction, calendar, valid_from, valid_to and a notes column;
- the blank-cell and after-midnight conventions;
- freeze panes, column widths and any conditional formatting needed to read a long table;
- how the master table groups lines and handles the sparse columns.

Output: a workbook contract section ready for the implementation spec.

## Answer

Resolved 2026-11-21.

### File and language

- Workbook: `euskotren_timetables_winter_2026_v1.xlsx` (season and version in the filename).
- Basque-primary content with Spanish aliases and notes, matching the PDFs.
- Sheet names are language-neutral: line code plus terminals. Excel forbids `/`, so `E2/T1` becomes `E2-T1` and `E3/L3` becomes `E3-L3`.

### Sheets

1. `README` — purpose, source PDFs, season, validity, generation date, legend, how cross-line rows work.
2. `Stops` — network-wide stop ID, Basque name, Spanish alias, lines served, stop-level notes.
3. `Calendars` — calendar ID, name, day types, `valid_from`, `valid_to`, notes.
4. `Manifest` — source PDF URL, checksum, fetch date, page count, season, `valid_from`, `valid_to`, generator version.
5. `Master` — one canonical row per service (see below).
6. `E1 Pasaia-Matiko`
7. `E1 Matiko-Pasaia`
8. `E2-T1 Hendaia-Lasarte`
9. `E2-T1 Lasarte-Hendaia`
10. `E3-L3 Lezama-Kukullaga`
11. `E3-L3 Kukullaga-Lezama`
12. `E4 Matiko-Bermeo`
13. `E4 Bermeo-Matiko`
14. `Frequency rules` — rule ID, source text, source PDF/page, expanded service IDs (including merged services), calendar, notes.
15. `Validation` — checks, expected/actual, status and notes, per ticket 09.

### Line/direction sheets: corridor views

- Each sheet is a **corridor view**, not a list of services owned by that line.
- A service appears in every line/direction sheet where it calls at **two or more consecutive stops in that sheet's travel direction** — i.e. it uses a shared segment. A single shared terminus is not enough.
- A service can therefore appear on several sheets. Rows are partial where the service leaves the line: times only at the stops it calls, blank elsewhere.
- Same service ID across all sheets; `Master` holds the canonical record.

### Shared trunks

- **E1 ↔ E2**: Pasaia–Errekalde.
- **E1 ↔ E4**: Lemoa–Matiko.
- **E1 ↔ E3/L3 ↔ E4**: Matiko–Kukullaga-Etxebarri.
- `Amorebieta Geltokia` (E1) and `Amorebieta Geralekua` (E4) are distinct stops, so the E1/E4 shared segment starts at Lemoa.
- Direction matching is by travel direction: a westbound service on the Bilbao core appears in the westbound sheet, not the eastbound one.

### Sheet layout

- Stops as columns in travel order; branch and through stops inline at their junction.
- Header block per stop column: `Stop ID`, `Basque name`, `Spanish alias`, `Branch/through marker`.
- Service metadata columns on the left: `Service ID`, `Primary line`, `Pattern`, `Calendar`, `Valid from`, `Valid to`, `Origin`, `Destination`, `Departure`, `Arrival`, `Notes`.
- One row per service; times in the stop cells.
- Calendars are stacked blocks — Weekday, Saturday, Sunday + holiday, Night — each with its own section header. The `Calendar` column repeats the calendar ID for filtering.
- Where the source merges Saturday with Sunday/holidays, that is one block; split only where the PDFs split.

### Master index

- One row per service: `Service ID`, `Primary line`, `Pattern`, `Appears in`, `Direction`, `Calendar`, `Valid from`, `Valid to`, `Origin`, `Destination`, `Departure`, `Arrival`, `Source PDF`, `Frequency rule(s)`, `Notes`.
- `Appears in` lists every line/direction sheet where the service has a segment, semicolon-separated.
- Service IDs are deterministic: `{line}-{direction}-{calendar}-{departure}`, e.g. `E1-PASAIA-MATIKO-WD-0535`.
- Stop IDs are network-wide (`S001`…), so shared stops stay one entity.

### Time and blank conventions

- 24-hour `HH:MM`.
- After-midnight times are `24:xx`/`25:xx` in the matrix; a separate `day_offset` field carries the same information in machine-readable exports.
- Blank means “does not stop”; `?` means “time not published”; no `>` or `-` in cells. The legend explains both.
- Conditional stops show their time only where they apply; the condition goes in the notes/stop notes.

### Print and readability

- Freeze the service metadata columns and the stop header rows.
- Repeat the header block on every printed page.
- Landscape, fit to width, per-line colour, autofilter on the metadata columns.
- Rotate the stop header rows 90° and use narrow columns; the `Stops` sheet carries the full names and aliases.
- Conditional formatting for conditional stops and notes.

### Provenance

- `README` records the source PDFs, checksums, season, validity, generation date and generator version.
- `Manifest` records each source PDF, checksum, fetch date and page count.
- `Frequency rules` records the original compressed rule and the expanded service IDs.
- `Stops` records stop-level notes.
- `Master` records the source PDF and frequency rule for each service.
- The workbook is generated output; corrections live in the sidecar file and are applied on every regeneration (ticket 10).
