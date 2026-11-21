# Inventory stops and canonical column order across in-scope PDFs

Type: research
Status: resolved
Blocked by:

## Question

Extract every stop header from the current winter-2026 PDFs for E1, E2/T1, E3+L3 and E4 (both directions and both day-type blocks), including footnote-only stops such as Altzola. For each line, produce:

- the ordered stop sequence from one extreme to the other, with branch stops placed inline at their junction;
- a canonical stop ID and Basque published name, plus the Spanish alias where present. There is no City entity: stops that share a municipality are distinct stations (`Eibar-Azitain`, `Eibar-Ardantza` and `Eibar` are three different stops), and the municipality label is composed into the name only when needed to disambiguate;
- a note of every direction-specific name and how it should be disambiguated;
- the source PDF, page and column coordinates that justify each stop.

This is the stop list the whole workbook is built on. Do not decide the Excel layout; supply the facts and a proposed order.

## Comments

- Claimed during charting by the PDF-inventory research subagent.
- 2026-11-21: subagent stopped; E1 and the E2 Hendaia → Amara section have been human-validated.
- Inventory report written to `research/01-stop-inventory.md`; machine-readable lists in `research/01-stop-headers.json`.
- Two identity questions remain: `Amorebieta Geltokia` vs `Amorebieta Geralekua`, and whether E3 calls at Matiko. Calling-pattern questions (Ola, Gaintxurizketa) go to ticket 06.

## Answer

Resolved 2026-11-21.

**Stop counts and order**

- E1: 50 stops on the current `Pasaia → Matiko` through service; the `Amara → Matiko` subset is 44.
- E2/T1: 23 stops, `Hendaia → Lasarte-Oria`; the reverse is the same sequence reversed.
- E3/L3: 16 stops on the combined `Lezama → Kukullaga` order; L3 is the 7-stop `Matiko → Kukullaga` pattern.
- E4: 25 stops, `Matiko → Bermeo`; the reverse is on the same PDF.

**Resolved identity questions**

- `Amorebieta Geltokia` and `Amorebieta Geralekua` are distinct stops on distinct lines: Geltokia on Bilbao–Donostia (E1), Geralekua on Bilbao–Bermeo (E4).
- E3 calls at `Matiko-Bilbao`.

**Shared trunks**

- E1 and E4 share Lemoa–Matiko.
- E1, E3/L3 and E4 share Matiko–Kukullaga-Etxebarri.
- E1's through service and E2 share Pasaia–Errekalde.

**Artifacts**

- Report: `research/01-stop-inventory.md`
- Machine-readable lists and header coordinates: `research/01-stop-headers.json`
- User corrections: `research/01-user-corrections.md`

**Deferred to the extraction-rules ticket** (06): whether all E3 services call at Ola (Sondika), and whether Gaintxurizketa is conditional on all E2 services.
