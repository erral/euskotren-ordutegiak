# Decide line order in the service sort key

Type: grilling
Status: resolved
Blocked by:
Parent: [Sort services in the output Excel timetable](../map.md)

## Question

`primary_line` is the third component of the canonical key. What order should the line codes use?

- (a) **Published workbook/sheet order**: `E1 → E2-T1 → E4 → E3-L3`. This matches the tab order and the order the lines are presented in the workbook.
- (b) **Lexicographic**: `E1 → E2-T1 → E3-L3 → E4`. Simple and language-independent, but puts E3-L3 before E4.
- (c) Some other order.

The choice affects `Master` row order directly and the cross-line tie-break inside every corridor sheet.

➡️ Recommendation: (a) published order, to match the sheet tabs and the reader's mental model.

## Answer

Resolved 2026-11-21.

The line order is the **published workbook/sheet order**:

`E1 → E2-T1 → E4 → E3-L3`

`Master` ordering and corridor cross-line tie-breaks use this sequence. Lexicographic order (`E1 → E2-T1 → E3-L3 → E4`) was rejected because it would not match the existing sheet-tab order.

## Comments

- Charted 2026-11-21. Waiting for the line-order decision.
- 2026-11-21: claimed for resolution.
- 2026-11-21: answered (a), published workbook/sheet order.
