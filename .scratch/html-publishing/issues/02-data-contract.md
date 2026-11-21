# Decide the `services.json` data contract

Type: grilling
Status: resolved
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What should the machine-readable site data contain and look like?

At minimum the site needs metadata, lines, directions, calendars, stops, corridors and every service with its stop times. The open choices are how much provenance to include and whether the JSON is the single source for the Master’s client-side filtering.

- (a) One versioned `services.json` with `meta`, `lines`, `calendars`, `stops`, `corridors` and a canonically ordered `services` array; each service carries its stop times, notes, pattern and corridor membership. No PDFs, no internal validation evidence.
- (b) One JSON per line/direction, loaded on demand.
- (c) No JSON: all filtering is server-rendered into static pages.

➡️ Recommendation: (a) one versioned `services.json`. It is simpler to validate, small enough at ~2,200 services, and lets the Master filter without extra requests.

## Answer

Resolved 2026-11-21.

One versioned `/data/services.json` with this top-level shape:

- `schema_version` — integer, incremented on breaking changes.
- `meta` — season, validity, generated time, generator version and the source manifest (label, official URL, SHA-256).
- `lines` — line code, slug, name and directions (name + slug).
- `calendars` — calendar id, slug, Basque/Spanish labels and canonical order.
- `stops` — stable stop id, Basque name and line memberships.
- `corridors` — sheet name, line, direction, direction slug and ordered stop columns.
- `services` — canonically ordered array; each service carries `service_id`, `primary_line`, `direction`, `calendar`, `pattern`, `origin`, `destination`, `departure`, `arrival`, `appears_in`, `frequency_rule_ids`, `notes` and `stop_times` (`stop_name`, `time`, `disposition`, `day_offset`).

The array order is the canonical service order; clients may rely on it. The file excludes the source PDFs and the internal validation/provenance evidence.

## Comments

- Charted 2026-11-21. Waiting for the data-contract decision.
- 2026-11-21: claimed for resolution.
- 2026-11-21: answered (a), one versioned `services.json`.
