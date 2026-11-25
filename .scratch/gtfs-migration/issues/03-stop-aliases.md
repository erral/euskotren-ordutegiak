# Decide stop alias and canonical-name mapping

Type: grilling
Status: resolved
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

How should GTFS stops map to the project's canonical stops and display names?

Cover at least:

- **Source stop**: use the GTFS `parent_station` (location type 1) as the canonical station; ignore platforms, entrances and generic nodes.
- **Alias table**: map GTFS names to the project's canonical Basque names (`Arroa-Zestoa` → `Arroa (Zestoa)`, `Bentaberri-Donostia` → `Benta-Berri (Donostia)`, etc.).
- **Failure mode**: fail the build on any GTFS stop used by the four lines that has no alias.
- **Registry**: keep `STOP_REGISTRY` and the existing display order; do not rename canonical stops to GTFS names.
- **E3a**: exclude its stops for the first migration; if E3a is added later, extend the registry and alias table.
- **Validation**: every in-scope GTFS stop must map to exactly one canonical stop.

➡️ Recommendation: parent-station mapping plus an explicit alias table, with a hard failure on unmapped in-scope stops and no changes to the canonical names or display order.

## Answer

Resolved 2026-11-25. All recommendations accepted.

- **Source stop**: map the GTFS `parent_station` (location type 1, `StopPlace`) to the project's canonical `Stop`. Resolve each `stop_times.stop_id` to its parent station; ignore Quay/platform, entrance and generic-node records.
- **Alias table**: a dedicated `euskotren_timetable/gtfs_stops.py` table keyed by GTFS `parent_station` ID, with the GTFS name recorded for diagnostics and the canonical name as the value (for example `ES:Euskotren:StopPlace:2613:` → `Arroa (Zestoa)`). The committed mapping is explicit and reviewed; a generated draft may seed it, but no fuzzy matching at runtime.
- **Failure mode**: the build fails if an in-scope trip uses a stop with no parent station or no alias. Out-of-scope stations are excluded explicitly; E3a is excluded before mapping.
- **Registry**: keep `STOP_REGISTRY`, the canonical Basque names and the existing display order; do not rename to GTFS spellings.
- **Validation**: every in-scope GTFS parent station maps exactly once, and every canonical stop used by the four lines has a mapping. This is a hard CI/build check.

## Comments

- Charted 2026-11-25.
- 2026-11-25: claimed and resolved. The user accepted all recommendations.
