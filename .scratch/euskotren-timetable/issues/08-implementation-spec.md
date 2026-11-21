# Write the implementation spec

Type: task
Status: resolved
Blocked by: 01, 03, 04, 05, 06, 07, 09, 10, 11

## Question

Assemble the destination spec from the resolved tickets:

- the canonical stop list and column order per line and direction;
- the normalized data model and extraction approach proven by the prototype;
- the footnote, branch and limited-stop rules;
- the workbook contract;
- the calendar and day-type model;
- the validation and refresh workflow, or explicit open items;
- phased delivery: weekdays, then Saturdays, then Sundays/holidays.

The spec is the map's final artifact; the production build is a separate effort.

## Answer

Resolved 2026-11-21. The implementation spec is at [`spec.md`](../spec.md).

It assembles:

- the canonical stop lists and shared trunks;
- the normalized data model;
- the extraction pipeline: manifest, coordinate parsing, full-line/partial-table merge, footnotes, frequency expansion, calendars and cross-line membership;
- the workbook contract: sheets, corridor views, master index, time/blank conventions, print and provenance;
- validation, refresh and versioning;
- phased delivery and acceptance criteria;
- open items and the production build backlog.
