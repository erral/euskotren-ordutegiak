# Decide the HTML site structure and URL scheme

Type: grilling
Status: open
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What page hierarchy and URL scheme should the generated site use?

- (a) **Static views with stable slugs**: an index, one page per line/direction/calendar, a searchable Master, JSON data and a workbook download. Example paths: `/`, `/line/e1/pasaia-matiko/weekday.html`, `/master.html`, `/data/services.json`, `/downloads/euskotren_timetables.xlsx`.
- (b) **Per-line pages with calendar tabs**: one page per line/direction, calendars switched in-page.
- (c) **One filterable page** for everything.

The scheme must work under a GitHub project path (`https://<owner>.github.io/<repo>/`), so links should be relative and deep-linkable.

➡️ Recommendation: (a) static views with stable slugs. Every timetable has a direct URL, the Master stays a separate lookup page, and relative links work under a project path.

## Comments

- Charted 2026-11-21. Waiting for the structure and URL decision.
