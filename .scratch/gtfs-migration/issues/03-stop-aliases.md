# Decide stop alias and canonical-name mapping

Type: grilling
Status: open
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

## Comments

- Charted 2026-11-25.
