# Decide calendar, route and output scope for a GTFS-based pipeline

Type: grilling
Status: resolved
Blocked by: 04
Parent: [Evaluate Euskotren GTFS as a timetable source](../map.md)

## Question

Once the source-of-truth model is chosen:

- Should the pipeline include the GTFS-only **E3a Lutxana–Sondika** branch, and should **T0 + T1** be merged under the current E2-T1 line or exposed separately?
- Should it model the GTFS **date-specific calendars** (holiday exceptions) and add a date picker, or derive the existing `WD/SA/SU/WE/FN/SN` calendars and lose the date exceptions?
- Should the workbook and wide HTML timetable stay the primary outputs, or should GTFS enable new views (date-based, route-based, live-style)?
- Should trams, the funicular and FCC remain out of scope?

➡️ Recommendation: keep the current four lines and the wide workbook/HTML as the first migration target; merge T0+T1 under E2-T1; include E3a only if it fits the existing corridor model; derive the existing day-type calendars for the first cut and treat date-specific output as a follow-up.

## Answer

Resolved 2026-11-25. All recommendations accepted.

- **Route and line scope**: keep the current four lines (E1, E2-T1, E4, E3-L3). Merge GTFS T0+T1 under E2-T1. Defer E3a (Lutxana–Sondika) to a later GTFS iteration. Keep trams, the funicular and FCC out of scope.
- **Calendar model**: derive the existing `WD/SA/SU/WE/FN/SN` calendars from GTFS for the first migration; retain GTFS `service_id` / `calendar_dates` information in the adapter for a later date-specific view.
- **Output scope**: keep the current workbook and wide HTML timetable as the primary outputs; add no new user-facing views in the first migration.
- **Deferred**: E3a, date-specific calendars/date picker, and new views are follow-ups after the GTFS adapter is proven.

## Comments

- Charted 2026-11-25. Blocked by the source-of-truth decision.
- 2026-11-25: [Decide the timetable source of truth and refresh policy](04-source-of-truth.md) resolved with option (a); this ticket is now on the frontier.
- 2026-11-25: claimed and resolved. The user accepted all scope recommendations.
