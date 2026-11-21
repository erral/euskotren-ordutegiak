# Settle the domain model for lines, branches and services

Type: grilling
Status: resolved
Blocked by:

## Question

Confirm the canonical vocabulary and relationships for the workbook: Line → Direction → trunk stop sequence + branches → Service → Stop time, with Calendar → Season and Day type. In particular:

- Is "service" the canonical term for one train run, or should it be "trip"?
- How is a branch represented relative to the trunk, and how is a service's calling pattern recorded?
- What identifies a stop when the published name repeats (for example the several Bilbao and Donostia columns)?
- What is the minimum normalized record set needed to render the wide table?

Update `GLOSSARY.md` with the resolved terms; keep implementation detail out of it.

## Answer

Resolved 2026-11-21.

- **Service** is the canonical term for one scheduled train run. `trip` is only a GTFS-alignment alias.
- **No City entity.** Only stops matter. Stops that share a municipality are distinct stations and are modelled separately: `Eibar-Azitain`, `Eibar-Ardantza` and `Eibar` are three different stops. The municipality label is composed into a stop's canonical name only when needed to disambiguate it, never modelled as an entity.
- **Display order vs calling pattern.** Each line and direction has a display order of stop columns, with branch stops inline at their junction. Each service has its own calling pattern: the ordered stops it actually calls at. The normalized records keep the calling pattern; the wide table uses the display order. An out-and-back double call would be an exception to flag if the inventory finds one.
- **Frequency rules expand.** Source notations such as `5:50 > 19:50, every 1h` and `every 30 min` become one explicit service per departure. The original rule is retained as provenance.
- **Blank means "does not stop".** Both `>` (passes without stopping) and `-` (does not serve) render blank in the wide table. The parser may retain the source symbol as provenance, but the published matrix has no cell marker.
- **Night services are a distinct day type.** The `Saturday night → Sunday` block is its own service group with a day offset; it is not folded into ordinary Saturday.
- **Minimum normalized set:** Stop; Line; Direction; Line stop (display order + branch marker); Branch; Service (line, direction, day type, season, origin, destination, notes); Stop time (service, stop, sequence, time, day offset, disposition); Calendar (season, day type, valid dates); Frequency rule (source rule + expanded services). No City entity.
