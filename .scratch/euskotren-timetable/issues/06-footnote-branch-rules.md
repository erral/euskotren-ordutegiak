# Generalize the footnote, branch and limited-stop extraction rules

Type: grilling
Status: resolved
Blocked by: 01, 03

## Question

Turn the Altzola rule into a general extraction policy:

- how to detect footnote-only stops and map their listed times to the correct service rows;
- how to mark branch columns and services that skip stops or short-turn;
- how to handle direction-specific footnotes and exceptions, including the E4 branches and the E3/L3 services;
- how to represent through-service patterns such as E1 Pasaia → Matiko, whose Pasaia–Amara section belongs to E1 and overlaps E2;
- how to merge guaranteed-stop sections that the full-line table omits, using partial tables (e.g. Pasaia → Zumaia);
- how to split a service whose destination varies by calendar into one row per calendar (e.g. E4's 22:12: Bermeo on Saturdays, Gernika on Sundays/holidays);
- what goes in the notes column versus what becomes a real column.

Output: rules the parser and the workbook contract can both use.

## Answer

Resolved 2026-11-21.

### Footnote mapping

- For a footnote-only stop between A and B, insert each footnote time into the service row whose times at A and B **bracket** it.
- Require exactly one match; flag zero or multiple matches for manual review.
- Never infer a time from a frequency pattern unless the frequency rule is explicitly expanded (ticket 11).

### Footnote types

- **Conditional stop** → real column; times only where applicable; condition in `Stops`.
- **Frequency footnote** → expand to explicit services (ticket 11).
- **Destination variant** → split into one service per calendar (ticket 07).
- **Special service / holiday eve** → calendar (ticket 07).
- **Train change or operational note** → `Notes` column.
- **One-off specials** (football extras) → out of scope.

### Branch, through, short-turn and limited-stop

- Branch stops are inline at their junction; services that do not call leave blanks.
- Through services appear in every corridor they traverse (ticket 05); partial rows are normal.
- Short-turn services carry `Pattern = short-turn`, use their real origin and destination, and leave blanks outside their run.
- Limited-stop services carry `Pattern = limited-stop`; blanks show the skipped stops.
- L3 services carry `Pattern = L3`; E3 services `Pattern = E3`; full-line services `Pattern = full`.
- `Pattern` is a filterable field in `Master` and each corridor sheet.

### Guaranteed-stop sections

- Parse the full-line table and the partial table for the guaranteed-stop section.
- Match services by their time at the section boundary (first and last shared stop).
- Merge the partial times into the full-line row.
- If there is no partial match, leave the intermediate stops as `?` (time not published) — never blank and never guessed.

### Conditional stops

- Altzola, Gaintxurizketa, Ola and any future conditional stop are real columns.
- Times only on the services that call; the condition is recorded in `Stops` notes.

### Notes versus real columns

- Any stop in the stop list is a real column.
- Service-level exceptions — train change at Amorebieta Geltokia, special-service notes, destination variants — go in `Notes`.
- Stop-level conditions go in `Stops`.
- One-off special services stay out of scope.

### Calendar-dependent destinations

- Split into one service row per calendar.
- Service IDs include the calendar: `E4-MATIKO-BERMEO-SA-2212` versus `E4-MATIKO-BERMEO-SU-2212`.
- Each row has a single origin and destination.
