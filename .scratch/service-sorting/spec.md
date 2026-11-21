# Service sorting specification

Status: written 2026-11-21. Implementation is a separate effort.

## Purpose

Define one deterministic order for service rows in the output Excel workbook, so that regenerating the workbook never reshuffles equal-time services and so that `Master` and the corridor sheets use a single, explainable contract.

## Scope

Applies to:

- `Master`
- `E1 Pasaia-Matiko`
- `E1 Matiko-Pasaia`
- `E2-T1 Hendaia-Lasarte`
- `E2-T1 Lasarte-Hendaia`
- `E4 Matiko-Bermeo`
- `E4 Bermeo-Matiko`
- `E3-L3 Lezama-Kukullaga`
- `E3-L3 Kukullaga-Lezama`

Everything else — `Frequency rules`, `Validation`, `Calendars`, `Stops`, `Manifest`, `Coverage`, `README`, `Source notes` — is outside this specification. The sheet-tab order is also outside it.

## Terms

- **Service order**: the canonical order of service rows in a timetable sheet. It is a presentation order, not part of service identity.
- **Departure**: the first timed stop of a service. It is stored on the extended clock, so an after-midnight service may read `24:xx` or `25:xx`.
- **Own line**: the line a corridor sheet belongs to. A corridor sheet may also contain services whose `primary_line` is a different line, because they share a trunk. A corridor sheet's own line is its line code.

## Canonical key

### Calendar order

```
WD → SA → SU → WE → FN → SN
```

Rationale: preserve the source day-type grouping; `WE` is the combined Saturday + Sunday + holiday calendar and follows the split `SA`/`SU` calendars; night calendars come last.

### Departure

`departure` is the first timed stop. Compare it with the same 24-hour-plus extended clock used for display:

- `23:45` is earlier than `24:00`.
- `24:00` is earlier than `25:37`.
- Do not use wall-clock parsing that wraps after midnight.

### Line order

```
E1 → E2-T1 → E4 → E3-L3
```

This is the published workbook/sheet order, not lexicographic order. Lexicographic order (`E1 → E2-T1 → E3-L3 → E4`) is rejected because it would not match the corridor tab order.

### Direction order

Within a line, use the published order:

| Line | First direction | Second direction |
|---|---|---|
| E1 | `Pasaia-Matiko` | `Matiko-Pasaia` |
| E2-T1 | `Hendaia-Lasarte` | `Lasarte-Hendaia` |
| E4 | `Matiko-Bermeo` | `Bermeo-Matiko` |
| E3-L3 (E3 branch) | `Lezama-Kukullaga` | `Kukullaga-Lezama` |
| E3-L3 (L3 local) | `Matiko-Kukullaga` | `Kukullaga-Matiko` |

E3-L3 is one primary line carrying both patterns: the E3 branch directions keep the published sheet order, then the L3 local directions follow.

### Final tie-breaker

`service_id`, ascending. Service IDs are unique across the current 2,227 services, and the full key has no duplicate rows. If a future regeneration produces duplicate service IDs, validation must fail rather than fall back to insertion order.

## `Master`

`Master` is a flat table:

- no section-header rows;
- the `Calendar` column carries the calendar;
- the existing AutoFilter is kept;
- rows are ordered by the **master key**:

```
calendar_rank
→ departure_minutes
→ line_rank
→ direction_rank
→ service_id
```

No own-line rule applies in `Master`.

## Corridor sheets

Corridor sheets keep their current structure:

- a section header per non-empty calendar, written in calendar order;
- merged stop headers and merged metadata headers;
- no AutoFilter and no Excel Table.

Within each calendar block, rows are ordered by the **corridor key**:

```
departure_minutes
→ own_line_rank
→ line_rank
→ direction_rank
→ service_id
```

where `own_line_rank` is:

- `0` when `service.primary_line` equals the corridor sheet's line;
- `1` otherwise.

`own_line_rank` is a tie-break **after departure**, not before it. A cross-line service at `05:28` still comes before an own-line service at `05:35`; the own-line rule only decides the order when two services share a departure.

The calendar is fixed by the block, so it is not repeated in the within-block comparison. `direction_rank` is included for completeness; a corridor sheet normally contains one direction.

### Example

In `E1 Pasaia-Matiko` at weekday `05:35`:

1. the E1 service (`own_line_rank = 0`);
2. the E2-T1 service (`own_line_rank = 1`).

In `E2-T1 Hendaia-Lasarte` at the same departure:

1. the E2-T1 service (`own_line_rank = 0`);
2. the E1 service (`own_line_rank = 1`).

In `Master` at the same departure:

1. E1 (`line_rank` before E2-T1);
2. E2-T1.

## Night services

The night calendars `FN` and `SN` follow the same key. Within `SN`, `23:45` sorts before `24:00`, and `24:00` sorts before `25:37`. The calendar block still separates `SN` from `WE` and `WD`.

## Documentation

The workbook documents the order with a short note on the `README` sheet only. The detailed rules live in this spec.

Suggested note:

> Services are ordered by operating calendar, departure time, line and direction; corridor sheets put their own line first when services share a departure. Night times use the extended clock (`24:xx`/`25:xx`).

No separate `Sort order` sheet, no `Sort key` column, and no `Coverage` note.

## Edge cases

- **Equal departure, same line and direction**: the service ID decides. This is the normal case for frequency-expanded and explicit services that overlap.
- **A service appears in several corridor sheets**: each sheet applies its own `own_line_rank`. The same service can be own-line in one sheet and cross-line in another.
- **Short-turns and refuerzos**: they sort by their own departure; their destination does not affect the key.
- **After-midnight services**: use the extended clock. Do not re-sort them by wall-clock time.
- **`?` stops**: a `?` stop is not a time and never supplies the departure. The departure is the first real time.
- **Unknown calendar, line or direction**: validation must fail; the rank tables are exhaustive.
- **No timed stop**: validation must fail; every service must have a departure.

## Validation

A later implementation must add:

1. **Unit tests for the key functions**: calendar rank, line rank, direction rank, extended departure, own-line rank, service-ID tie-break.
2. **Golden rows**:
   - `Master` weekday `05:35`: E1 before E2-T1.
   - `E1 Pasaia-Matiko` weekday `05:35`: E1 before E2-T1.
   - `E2-T1 Hendaia-Lasarte` weekday `05:35`: E2-T1 before E1.
   - `SN` night: `23:45` before `24:00`, and `24:00` before `25:37`.
3. **Regeneration checks**:
   - `Master` has no section-header rows and remains filtered.
   - Every corridor block appears in calendar order.
   - Every service row is non-decreasing under its sheet's key.
   - Corridor sheets have no AutoFilter.
4. **Duplicate-ID check**: fail if service IDs are not unique.

## Implementation notes for the later effort

- Put the rank tables and key functions in one module (for example `service_order.py`) so `Master` and corridor rendering share the same contract.
- Reuse the existing extended-clock helper (`to_minutes`) rather than `datetime.time`.
- Sort `Master` in the master renderer, and sort each calendar group in the corridor renderer. Do not change `assign_membership`, service IDs, stop order, or sheet-tab order.
- Keep the `Master` AutoFilter. Do not add filters or Excel Tables to the corridor sheets.

## Out of scope

- Changing the generator in this effort.
- Interactive Excel sorting or filters on corridor sheets.
- Reordering sheet tabs.
- Sorting the non-timetable sheets.
- Stop-column or display order.
- Machine-readable exports, API ordering or future seasons.
- Spanish aliases.
