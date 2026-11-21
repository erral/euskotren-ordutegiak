# Prototype: parse one E1 weekday direction into stop-time records

Type: prototype
Status: resolved
Blocked by:

## Question

Build a throwaway parser for the E1 weekday block in one direction that:

- maps the rotated station headers to columns using their coordinates (no OCR, no naive text order);
- extracts each service row as an ordered list of (stop, time) records;
- unfolds the Altzola footnote into Altzola stop times on the matching services;
- emits the normalized records and a rendered wide table for visual comparison with the PDF.

Validate the output against the source PDF. Link the prototype under `.scratch/euskotren-timetable/prototypes/`. The goal is to prove the extraction approach, not to generalize to every PDF.

## Comments

- Unblocked for E1 on 2026-11-21: the user validated the 45-stop E1 list, including `Kontxa-Zentroa` and `Benta-Berri`. The full inventory ticket still covers E2–E4 separately.
- Source for the proof: the current E1 PDFs under `https://euskotren.eus/eu/tren/ordutegiak`. Use the weekday block of one direction; note which PDF and page the output comes from.
- Prototype built at `prototypes/e1-weekday-parser/`; user confirmed `Traña Abadiño` is one stop and E1 Pasaia → Matiko is a through service.

## Answer

Resolved 2026-11-21. Prototype: `prototypes/e1-weekday-parser/`.

- Input: the current 21 November 2026 `E1 Pasaia → Matiko Bilbao` PDF, page 1, weekday block.
- Coordinate-based parse of the full-line table (42 columns) plus the `Pasaia → Zumaia` partial table (17 columns); no OCR.
- The 05:35 through service is reconstructed across all 50 stops. `Traña Abadiño` is one stop; `Altzola` is `>` (passes without stopping).
- E1 `Pasaia → Matiko` is a through service: the Pasaia–Amara Topo section belongs to E1, not a branch, and overlaps E2 geographically.
- Finding: the full-line table collapses guaranteed-stop sections, so the parser must merge partial tables. The partial table only covers 5:35, 6:05, 21:05 and 21:35; the other full-line services lack the intermediate Topo times in this PDF.
- Outputs: `e1_weekday_wide.csv`, `e1_weekday_0535.csv`, `e1_weekday_0535.md`.
