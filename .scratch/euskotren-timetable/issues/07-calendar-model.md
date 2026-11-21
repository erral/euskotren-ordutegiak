# Define the calendar and day-type model

Type: grilling
Status: resolved
Blocked by: 04

## Question

Decide how the workbook records when a timetable applies:

- day types: weekday, Saturday, Sunday/holiday, and the separate Saturday-night → Sunday group;
- the season and validity dates for winter 2026;
- where the holiday calendar comes from and how holiday services are selected;
- how special or exception services are represented, or explicitly excluded;
- the columns each service row carries for day type and validity.

Delivery order remains weekdays, then Saturdays, then Sundays/holidays.

## Answer

Resolved 2026-11-21.

- **Calendars are named service sets, not a fixed day-type enum.** Examples: Weekday; Saturday; Sunday + holiday; Saturday + Sunday + holiday; Friday night / holiday eve; Saturday night. Every service belongs to exactly one calendar.
- **Preserve the source grouping.** Where a PDF merges Saturday with Sunday/holidays, that is one calendar. Generate separate Saturday and Sunday/holiday views only where the source actually separates them. Build order: weekdays → weekend/holiday calendars → night calendars.
- **Service day and after-midnight times.** A service belongs to the day it starts. After-midnight times use `24:xx`/`25:xx` or an explicit `+1 day` offset; 00:30 on Sunday is part of Saturday's service day and night calendar.
- **Holiday eves are first-class.** A holiday-eve calendar is distinct from an ordinary Friday night; the holiday date list identifies the eves.
- **Holiday dates are deferred.** Phase one uses the "Sunday/holiday" calendar label; the actual Basque holiday dates are an external input for later date-specific views, not part of the timetable table.
- **Calendar-dependent services split.** When a service's destination differs by calendar (E4's 22:12: Bermeo on Saturdays, Gernika on Sundays/holidays), split it into one service row per calendar, each with a single origin and destination.
- **Validity and versioning.** Each timetable version carries `valid_from`, an open `valid_to` until superseded, `season = winter 2026`, and its source PDF. The 7 September 2026 and 21 November 2026 starts are separate versions.
