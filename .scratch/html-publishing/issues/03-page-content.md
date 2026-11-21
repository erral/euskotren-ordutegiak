# Decide the page content and table behaviour

Type: grilling
Status: resolved
Blocked by: 01, 02
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What does each page show, and how do the timetable tables behave?

Cover at least:

- **Index**: validity, last generated time, line/direction/calendar links, workbook download, source attribution.
- **Corridor page**: metadata header, calendar sections or tabs, stops as columns and services as rows, sticky header, horizontal scroll, stop search/filter, `?`/pass/not-served rendering, night `24:xx`/`25:xx` legend, anchors per service.
- **Master**: search and filter fields (line, calendar, origin, destination, departure, service ID), initial view, no-JS fallback.

➡️ Recommendation: corridor pages mirror the workbook’s calendar blocks; the Master starts with the full table and filters client-side; every service row gets a stable `#<service-id>` anchor; `?`, pass and not-served have distinct visible treatments.

## Answer

Resolved 2026-11-21. All three recommendations accepted.

- **Corridor pages** show one calendar per page, with a calendar switcher for the same line/direction. The header carries the line, direction, calendar, validity and generated time; the table is workbook-faithful, horizontally scrollable and every service row has a `#<service-id>` anchor. The first column scrolls with the table. A stop search box filters the services to those serving the matching stop(s). Source attribution and the workbook download link sit at the bottom.
- **Master** renders the full service table initially and filters client-side by line, calendar, origin, destination, departure and service ID. No pagination or virtual scrolling in the first version; the no-JS fallback shows the full table.
- **Cell states**: `?` for unpublished times in red, `>` for pass in a muted style, blank for not served. `FN`/`SN` pages carry a `24:xx`/`25:xx` and service-day legend.

## Comments

- Charted 2026-11-21. Blocked by the site-structure and data-contract tickets.
- 2026-11-21: claimed for resolution; both blockers resolved.
- 2026-11-21: answered “ok” to all three (interpreted “çok” as ok).
- 2026-11-21: refinement — corridor metadata columns (Service ID, Line, Pattern, Origin, Destination, Departure, Arrival) are hidden by default and revealed with a “show metadata” toggle. The Master remains a metadata index.
- 2026-11-21: refinement — corridor pages get a stop search box that filters services to those serving the matching stop(s) and highlights the stop columns.
- 2026-11-21: refinement — the first column no longer stays fixed while scrolling the table horizontally; the header remains sticky.
