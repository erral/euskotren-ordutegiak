# Decide direction order within each line

Type: grilling
Status: resolved
Blocked by:
Parent: [Sort services in the output Excel timetable](../map.md)

## Question

Within one line, `direction` is the fourth component of the canonical key. What order should the two directions use?

- (a) **Published sheet order**:
  - E1: `Pasaia-Matiko` → `Matiko-Pasaia`
  - E2-T1: `Hendaia-Lasarte` → `Lasarte-Hendaia`
  - E4: `Matiko-Bermeo` → `Bermeo-Matiko`
  - E3-L3: `Lezama-Kukullaga` → `Kukullaga-Lezama`
- (b) **Lexicographic** by direction string.
- (c) Some other order.

The choice affects `Master` ordering and the corridor cross-line tie-break whenever two different lines share the same departure and primary line order.

➡️ Recommendation: (a) published sheet order, so `Master` and the corridor tabs use the same direction sequence.

## Answer

Resolved 2026-11-21.

The direction order is the **published sheet order**:

- E1: `Pasaia-Matiko` → `Matiko-Pasaia`
- E2-T1: `Hendaia-Lasarte` → `Lasarte-Hendaia`
- E4: `Matiko-Bermeo` → `Bermeo-Matiko`
- E3-L3: `Lezama-Kukullaga` → `Kukullaga-Lezama`

`Master` uses this order when grouping each line's two directions. Lexicographic order was rejected because it would not match the corridor sheet-tab order.

## Comments

- Charted 2026-11-21. Waiting for the direction-order decision.
- 2026-11-21: claimed for resolution.
- 2026-11-21: answered (a), published sheet order.
- 2026-11-21: implementation surfaced the L3 local directions, which share the E3-L3 primary line. Extended the order with `Matiko-Kukullaga → Kukullaga-Matiko` after the E3 branch pair; spec updated.
