# Sort services in the output Excel timetable

Status: route clear — sorting specification written 2026-11-21.

## Destination

A written sorting specification for the workbook: one deterministic row order for services in `Master` and the eight corridor sheets, covering calendar order, departure and night-time handling, line and direction order, tie-breakers, and sheet-specific rules. Implementation is a separate effort.

## Notes

- **Effort type**: planning. The map resolves decisions; it does not change the workbook generator.
- **Issue tracker**: local markdown. This file is the map; tickets live in `issues/`. See `docs/agents/issue-tracker.md`.
- **Scope**: `Master` plus the eight corridor sheets (`E1 Pasaia-Matiko`, `E1 Matiko-Pasaia`, `E2-T1 Hendaia-Lasarte`, `E2-T1 Lasarte-Hendaia`, `E4 Matiko-Bermeo`, `E4 Bermeo-Matiko`, `E3-L3 Lezama-Kukullaga`, `E3-L3 Kukullaga-Lezama`).
- **Glossary**: [GLOSSARY.md](../../GLOSSARY.md), especially Service, Calendar, Service day and Service order.
- **Current behaviour**: `Master` is ordered `departure → primary line → direction`; corridor sheets are stacked by calendar and ordered by `departure` only. Corridor sheets have merged headers and no AutoFilter.

### Standing decisions (settled during charting)

1. One deterministic order is baked into the workbook; interactive Excel sorting is not required.
2. Base key: **calendar → departure → primary line → direction → service ID**.
3. Calendar order: `WD → SA → SU → WE → FN → SN`.
4. `departure` is the first timed stop; night services use the extended clock (`24:xx`, `25:xx`) so they sort after `23:xx`.
5. `Master` stays a flat table with a `Calendar` column; no section-header rows.
6. Corridor sheets keep their stacked calendar blocks and merged headers.
7. Corridor tie-break: the sheet's own line first, then `primary line → direction → service ID`.
8. Keep the existing `Master` AutoFilter; do not add filters or Excel Tables to the corridor sheets.
9. Service IDs are unique across the current 2,227 services, and the full key has no duplicate rows, so `service ID` is a safe final tie-breaker.

## Decisions so far

- [Decide line order in the service sort key](issues/01-line-order.md): published workbook/sheet order `E1 → E2-T1 → E4 → E3-L3`.
- [Decide direction order within each line](issues/02-direction-order.md): published sheet order for each line (e.g. E1 `Pasaia-Matiko` before `Matiko-Pasaia`); E3-L3 extends the branch pair with the L3 local directions.
- [Decide how the sort order is documented in the workbook](issues/03-sort-documentation.md): concise `README` note only; detailed rules live in the spec.
- [Write the service sorting specification](issues/04-write-sort-spec.md): spec written at [`spec.md`](spec.md); master and corridor keys, own-line tie-break, calendar/line/direction orders, night handling, validation and implementation boundary defined.

## Not yet specified

None. The specification covers the section structure, validation approach and golden-example format.

## Out of scope

- Implementing the sort in the generator; the destination is the spec, and implementation is a separate effort.
- Interactive Excel sorting or filters on the corridor sheets.
- Reordering the sheet tabs themselves.
- Sorting non-timetable sheets (`Frequency rules`, `Validation`, `Calendars`, `Stops`, `Manifest`, `Coverage`, `README`, `Source notes`).
- Stop-column or display order; this effort is service rows only.
- Machine-readable exports, API ordering or future seasons; the destination is the current Excel workbook contract.
- Spanish aliases; they are intentionally omitted.
