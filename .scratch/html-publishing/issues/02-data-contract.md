# Decide the `services.json` data contract

Type: grilling
Status: open
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What should the machine-readable site data contain and look like?

At minimum the site needs metadata, lines, directions, calendars, stops, corridors and every service with its stop times. The open choices are how much provenance to include and whether the JSON is the single source for the Master’s client-side filtering.

- (a) One versioned `services.json` with `meta`, `lines`, `calendars`, `stops`, `corridors` and a canonically ordered `services` array; each service carries its stop times, notes, pattern and corridor membership. No PDFs, no internal validation evidence.
- (b) One JSON per line/direction, loaded on demand.
- (c) No JSON: all filtering is server-rendered into static pages.

➡️ Recommendation: (a) one versioned `services.json`. It is simpler to validate, small enough at ~2,200 services, and lets the Master filter without extra requests.

## Comments

- Charted 2026-11-21. Waiting for the data-contract decision.
