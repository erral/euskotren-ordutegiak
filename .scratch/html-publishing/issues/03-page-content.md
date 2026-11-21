# Decide the page content and table behaviour

Type: grilling
Status: open
Blocked by: 01, 02
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What does each page show, and how do the timetable tables behave?

Cover at least:

- **Index**: validity, last generated time, line/direction/calendar links, workbook download, source attribution.
- **Corridor page**: metadata header, calendar sections or tabs, stops as columns and services as rows, sticky header/first columns, horizontal scroll, `?`/pass/not-served rendering, night `24:xx`/`25:xx` legend, anchors per service.
- **Master**: search and filter fields (line, calendar, origin, destination, departure, service ID), initial view, no-JS fallback.

➡️ Recommendation: corridor pages mirror the workbook’s calendar blocks; the Master starts with the full table and filters client-side; every service row gets a stable `#<service-id>` anchor; `?`, pass and not-served have distinct visible treatments.

## Comments

- Charted 2026-11-21. Blocked by the site-structure and data-contract tickets.
