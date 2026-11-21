# Define how extracted timetables are validated

Type: grilling
Status: resolved
Blocked by: 03

## Question

Decide the checks that make a parsed timetable trustworthy:

- visual comparison of the rendered table against the PDF;
- cross-direction and cross-day-type consistency checks;
- service-count and first/last-train checks;
- whether to compare against the official search engine and, if so, on which sample. Ticket 02 found it scriptable via a plain GET to `/eu/horarios/resultados`, but it exposes only boarding/alighting times, no intermediate stop times, no trip IDs and a ~31-day horizon; use it only as a spot-check (1–3 terminus-to-terminus services per line/day type), never as an oracle;
- how failures are recorded and reviewed.

Output: a validation checklist for the spec and the prototype.

## Answer

Resolved 2026-11-21.

### Validation layers

1. **Structural**
   - Every service has a monotonically increasing time sequence in travel order.
   - Stop order matches the sheet's display order.
   - No `>` or `-` in the matrix; only times, blank, or `?`.
   - Every stop in a matrix exists in `Stops`; every stop in `Stops` appears in at least one line.
   - Every service has a calendar, `valid_from`, `valid_to`, origin, destination and pattern.
   - `?` appears only in the expected unpublished set.
   - Every `Appears in` corridor has at least two consecutive stops in the service's direction.
   - Every service has at least two stops.
2. **Source**
   - Service counts per sheet and calendar match the PDF.
   - First and last service times match the PDF exactly.
   - Conditional stops — Altzola, Gaintxurizketa, Ola — are present where expected.
   - Visual matrix diff against the PDF for every sheet.
3. **Cross-direction and cross-calendar**
   - Service counts and first/last times per direction and calendar.
   - Night blocks use `day_offset` correctly.
   - Calendar-specific destination variants are distinct and complete.
4. **Search-engine spot-check**
   - 1–3 terminus-to-terminus services per line and day type, within the 31-day horizon.
   - Compare departure and arrival only.
   - No intermediate stops, trip IDs or holidays.
   - Never used as an oracle.

### Automated versus manual

- Structural, source and cross checks run automatically into a `Validation` sheet and a Markdown report.
- A human visually reviews every line/direction/calendar sheet at least once and spot-checks 3–5 services per sheet.
- Sign-off per sheet is required; unresolved failures block sign-off.

### Tolerances

- Service counts and first/last times require exact matches.
- Any mismatch fails.
- The `?` count must equal the expected unpublished set; a new `?` is a failure until reviewed.
- No guessing or interpolation.

### Failure record

- `Validation` columns: sheet, service ID, stop, check, expected, actual, status, notes.
- A Markdown report summarises pass/fail by sheet.
- Unresolved failures block sign-off.

### Regression

- Rerun the same checks on every regeneration.
- Compare against the previous baseline.
- Any new `?`, service-count change, first/last change or conditional-stop change is a failure until reviewed.
