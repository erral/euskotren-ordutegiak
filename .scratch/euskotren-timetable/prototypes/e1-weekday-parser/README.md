# E1 weekday prototype

Proves coordinate-based extraction on the current **21 November 2026** E1 `Pasaia → Matiko Bilbao` PDF.

## What it does

- Parses the full-line weekday table (services at 5:35, 6:35, 18:35, 19:35, 20:35).
- Parses the `Pasaia → Zumaia` partial table (17 columns) on the same page.
- Maps times to stops by word x-coordinate, not text order; no OCR.
- Merges the two tables for the 05:35 service.
- Emits:
  - `e1_weekday_wide.csv` — one row per full-line weekday service, stops as columns.
  - `e1_weekday_0535.csv` — normalized records for the merged 05:35 service.
  - `e1_weekday_0535.md` — vertical view of the merged 05:35 service.

## Result

- The 05:35 service is complete for **all 50 stops**.
- `Traña Abadiño` is a single stop, not two.
- `Altzola` is `>` — the train passes without stopping.

## Findings for the workbook

1. **The full-line table is not a complete stop matrix.** It has 42 columns, not 50. It omits stops where every train stops (the note says all trains stop from Pasaia to Aia-Orio). The parser must merge partial tables.
2. **The partial table only covers some services.** `Pasaia → Zumaia` has weekday services at 5:35, 6:05, 21:05 and 21:35. The full-line 05:35 merges cleanly; the other full-line services (6:35, 18:35, 19:35, 20:35) lack the intermediate Topo times because no matching partial row was found.
3. **E1 Pasaia → Matiko is a through service.** The Pasaia–Amara Topo section is part of E1, not a branch; it overlaps E2 geographically. The workbook must model through-service patterns, not just a single trunk per line.

## Reproduce

```bash
python3 parse_e1.py /path/to/E1_Pasaia_-_Matiko_4.pdf
```

The source PDF is the one linked as `E1 Pasaia - Matiko` on
`https://euskotren.eus/eu/tren/ordutegiak`.
