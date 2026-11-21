# Sort services in the output Excel timetable

Status: charted — 3 decision tickets open, spec task blocked.

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

<!-- one line per closed ticket, added when the ticket resolves -->

## Not yet specified

- The spec's section structure and whether it carries pseudocode or a reference implementation.
- How the order is validated (golden rows, regression tests, or a manual review checklist).
- How the spec should present its golden examples (inline table, appendix, or fixture file).

## Out of scope

- Implementing the sort in the generator; the destination is the spec, and implementation is a separate effort.
- Interactive Excel sorting or filters on the corridor sheets.
- Reordering the sheet tabs themselves.
- Sorting non-timetable sheets (`Frequency rules`, `Validation`, `Calendars`, `Stops`, `Manifest`, `Coverage`, `README`, `Source notes`).
- Stop-column or display order; this effort is service rows only.
- Machine-readable exports, API ordering or future seasons; the destination is the current Excel workbook contract.
- Spanish aliases; they are intentionally omitted.
