# Define the frequency-rule expansion rules

Type: grilling
Status: resolved
Blocked by: 01, 03

## Question

The PDFs compress repeating services into notations such as `5:50 > 19:50, every 1h`, `every 30 min`, and combined notes like `Elgoibartik / desde Elgoibar 1 h - Eibartik / desde Eibar 30 min`. Define:

- how to read each notation and identify the affected origin/destination block and day type;
- how to expand it into explicit services with correct times;
- how to handle overlaps, gaps, and services that fall outside the stated range;
- what provenance to keep so an expanded service can be traced back to its rule.

Output: frequency-expansion rules for the parser and the workbook contract.

## Answer

Resolved 2026-11-21.

### Notation grammar

- In a frequency note, `>` is a **range separator**, not the pass-through symbol.
- Parse each clause independently: start, end, interval (`1 h`, `30 min`, `15 min`, etc.) and optional origin prefix.
- Support `MAIZTASUNA`, `FRECUENCIA`, `M.-F.` and bilingual prefixes such as `Elgoibartik / desde Elgoibar`.

### Expansion

- Generate departures at start + n × interval, inclusive of the end time.
- Merge generated departures with explicit rows in the same block.
- Explicit rows win; deduplicate by departure time.
- Flag gaps or times that do not align with the interval.

### Multiple clauses and origins

- Parse each clause independently and generate its own service set.
- If two clauses produce services whose **shared-stop times match**, merge them into one service row: the earlier origin becomes the service origin, the later origin becomes an intermediate stop, and both rule IDs are retained.
- If the times do not match, keep separate rows.
- This prevents duplicate rows for the same physical train while preserving different origins.

### Stop-frequency versus service-frequency

- Notes such as `Gaintxurizketan geldialdia 30 minutik behin` are conditional-stop notes, not frequency rules.
- They never generate services.

### Provenance

- Every expanded service carries a rule ID, source text, source PDF/page and block.
- A merged service carries all contributing rule IDs.
- The `Frequency rules` sheet lists each rule and its expanded service IDs.

### Midnight and validation

- Ranges crossing midnight use a day offset.
- Validate by count, first/last time and comparison with explicit rows; flag mismatches.
