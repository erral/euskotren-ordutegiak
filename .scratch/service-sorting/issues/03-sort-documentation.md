# Decide how the sort order is documented in the workbook

Type: grilling
Status: resolved
Blocked by:
Parent: [Sort services in the output Excel timetable](../map.md)

## Question

Where should a reader learn the canonical order of service rows?

- (a) A short note on the `README` sheet only; the detailed rules live in the spec.
- (b) A separate `Sort order` sheet listing the full key and examples.
- (c) A `Sort key` column on `Master` and/or the corridor sheets.
- (d) A note in `Coverage`, next to the included/pending matrix.

The trade-off is discoverability versus a second source of truth and extra columns on the timetable sheets.

➡️ Recommendation: (a) a concise `README` note plus the spec. Keep the timetable sheets clean and the rules in one canonical document.

## Answer

Resolved 2026-11-21.

The canonical order is documented as a **concise note on the `README` sheet only**. The detailed rules live in the sorting specification. No separate `Sort order` sheet, no `Sort key` column, and no `Coverage` note.

This keeps the timetable sheets clean and avoids a second source of truth.

## Comments

- Charted 2026-11-21. Waiting for the documentation decision.
- 2026-11-21: claimed and resolved with option (a), README note.
