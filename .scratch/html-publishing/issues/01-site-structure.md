# Decide the HTML site structure and URL scheme

Type: grilling
Status: resolved
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What page hierarchy and URL scheme should the generated site use?

- (a) **Static views with stable slugs**: an index, one page per line/direction/calendar, a searchable Master, JSON data and a workbook download. Example paths: `/`, `/line/e1/pasaia-matiko/weekday.html`, `/master.html`, `/data/services.json`, `/downloads/euskotren_timetables.xlsx`.
- (b) **Per-line pages with calendar tabs**: one page per line/direction, calendars switched in-page.
- (c) **One filterable page** for everything.

The scheme must work under a GitHub project path (`https://<owner>.github.io/<repo>/`), so links should be relative and deep-linkable.

➡️ Recommendation: (a) static views with stable slugs. Every timetable has a direct URL, the Master stays a separate lookup page, and relative links work under a project path.

## Answer

Resolved 2026-11-21.

The site uses **static views with stable slugs**:

- `/` — index with validity, generated time, line/direction/calendar links and the workbook download.
- `/line/<line-slug>/<direction-slug>/<calendar-slug>.html` — one page per timetable.
- `/master.html` — searchable Master.
- `/data/services.json` — machine-readable data for the Master.
- `/downloads/<workbook>.xlsx` — workbook download.

Slug scheme:

- lines: `e1`, `e2-t1`, `e4`, `e3-l3`
- directions: `pasaia-matiko`, `matiko-pasaia`, `hendaia-lasarte`, `lasarte-hendaia`, `matiko-bermeo`, `bermeo-matiko`, `lezama-kukullaga`, `kukullaga-lezama`
- calendars: `weekday`, `saturday`, `sunday-holiday`, `weekend`, `friday-night`, `saturday-night`

All links are relative so the site works under a GitHub project path. Each service row is anchored as `#<service-id>`.

## Comments

- Charted 2026-11-21. Waiting for the structure and URL decision.
- 2026-11-21: claimed for resolution.
- 2026-11-21: answered (a), static views with stable slugs.
