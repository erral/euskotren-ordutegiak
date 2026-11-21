# Stop inventory — E1, E2/T1, E3/L3, E4

- **Researched**: 2026-11-21 against the current winter-2026 PDFs.
- **Canonical source**: the official PDFs. The 2026 network schematic is a cross-check but predates the 21 November 2026 Donostia stations.
- **Method**: coordinate-based header extraction (`pdftotext -bbox-layout`) plus visual checks of the rendered PDFs; no OCR. E3/L3 header text is fragmented in the PDF, so its names come from the line diagram on page 1.
- **Machine-readable lists**: `01-stop-headers.json`.

## Canonicalisation rules

- There is no City entity. Stops that share a municipality are distinct stations.
- `Traña Abadiño` is one stop, not `Traña` + `Abadiño`.
- `Amara Donostia` merges E1's `AMARA / DONOSTIA` and E2's `DONOSTIA/SAN SEBASTIÁN AMARA`.
- `Zazpikaleak/Casco Viejo` is canonical.
- Keep the published Basque name; add the Spanish alias where the PDF prints one.

## E1 — Pasaia/Amara ↔ Matiko-Bilbao

Current 21 November through service, `Pasaia → Matiko Bilbao`, 50 stops:

1. Pasaia
2. Altza (Donostia)
3. Herrera (Donostia)
4. Intxaurrondo (Donostia)
5. Loiola (Donostia)
6. Anoeta (Donostia)
7. Amara Donostia
8. Kontxa-Zentroa (Donostia)
9. Benta-Berri (Donostia)
10. Lugaritz (Donostia)
11. Añorga (Donostia)
12. Errekalde (Donostia)
13. Usurbil
14. Aia-Orio
15. San Pelaio (Zarautz)
16. Zarautz
17. Zumaia
18. Arroa (Zestoa)
19. Deba
20. Mendaro
21. Altzola (Elgoibar) — conditional
22. Toletxegain (Elgoibar)
23. Elgoibar
24. Azitain (Eibar)
25. Eibar
26. Ardantza (Eibar)
27. Amaña (Eibar)
28. Unibertsitatea (Eibar)
29. San Lorentzo (Ermua)
30. Errotabarri (Ermua)
31. Ermua
32. Zaldibar
33. Berriz
34. Traña Abadiño
35. Durango
36. Euba (Amorebieta)
37. Amorebieta Geltokia
38. Lemoa
39. Bedia
40. Usansolo
41. Zuhatzu (Galdakao)
42. Ariz (Basauri)
43. Etxebarri
44. Kukullaga-Etxebarri
45. Otxarkoaga (Bilbao)
46. Txurdinaga (Bilbao)
47. Zurbaranbarri (Bilbao)
48. Zazpikaleak/Casco Viejo (Bilbao)
49. Uribarri (Bilbao)
50. Matiko-Bilbao

- The `Amara → Matiko` subset drops Pasaia, Altza, Herrera, Intxaurrondo, Loiola and Anoeta, leaving 44 stops.
- `Altzola` is conditional: 8:56, 12:56, 19:56 and 21:56.
- The Pasaia–Amara section is part of the through service and overlaps E2 geographically.
- Sources: `E1 Pasaia - Matiko_4.pdf`, page 1 (21 November); `E1 Amara-Matiko.pdf` (7 September) for the Amara variant.

## E2/T1 — Hendaia ↔ Lasarte-Oria

`Hendaia → Lasarte-Oria`, 23 stops:

1. Hendaia
2. Irun Ficoba
3. Irun
4. Belaskoenea (Irun)
5. Bentak (Irun)
6. Gaintxurizketa (Lezo) — conditional, every 30 minutes
7. Oiartzun
8. Fanderia (Errenteria)
9. Errenteria
10. Galtzaraborda (Errenteria)
11. Pasaia
12. Altza (Donostia)
13. Herrera (Donostia)
14. Intxaurrondo (Donostia)
15. Loiola (Donostia)
16. Anoeta (Donostia)
17. Amara Donostia
18. Kontxa-Zentroa (Donostia)
19. Benta-Berri (Donostia)
20. Lugaritz (Donostia)
21. Añorga (Donostia)
22. Errekalde (Donostia)
23. Lasarte-Oria

- The reverse direction is the same sequence reversed.
- Kontxa-Zentroa and Benta-Berri are the new Donostia stations opened on 21 November 2026.
- Sources: `T1_Hendaia-Lasarte.pdf` and `T1_Lasarte-Hendaia.pdf` (21 November); `E2_*` 7 September variants for comparison.

## E3/L3 — Lezama ↔ Kukullaga-Etxebarri

Combined display order, `Lezama → Kukullaga-Etxebarri` via Matiko, 16 stops:

1. Lezama
2. Kurtzea (Lezama)
3. Zamudio
4. Lekunbiz (Zamudio)
5. Derio
6. Elotxelerri (Loiu)
7. Larrondo (Loiu)
8. Sondika
9. Ola (Sondika)
10. Matiko-Bilbao
11. Uribarri (Bilbao)
12. Zazpikaleak/Casco Viejo (Bilbao)
13. Zurbaranbarri (Bilbao)
14. Txurdinaga (Bilbao)
15. Otxarkoaga (Bilbao)
16. Kukullaga-Etxebarri

- **L3 pattern**: Matiko-Bilbao → Kukullaga-Etxebarri, stops 10–16.
- **E3 pattern**: Lezama → Kukullaga-Etxebarri via Matiko, all 16 stops.
- The E3/L3 PDF has four direction tables: Matiko ↔ Kukullaga (L3) and Lezama ↔ Kukullaga (E3).
- Source: `E3_L3_CARTEL_50x70_Invierno_2026_2.pdf`, page 1 diagram and tables.

## E4 — Matiko-Bilbao ↔ Bermeo

`Matiko-Bilbao → Bermeo`, 25 stops:

1. Matiko-Bilbao
2. Uribarri (Bilbao)
3. Zazpikaleak/Casco Viejo (Bilbao)
4. Zurbaranbarri (Bilbao)
5. Txurdinaga (Bilbao)
6. Otxarkoaga (Bilbao)
7. Kukullaga-Etxebarri
8. Etxebarri
9. Ariz (Basauri)
10. Zuhatzu (Galdakao)
11. Usansolo
12. Bedia
13. Lemoa
14. Amorebieta Geralekua
15. Zugastieta (Muxika)
16. Muxika
17. Lurgorri (Gernika)
18. Gernika
19. Institutua (Gernika)
20. Forua
21. S. Kristobal (Busturia)
22. Axpe (Busturia)
23. Itsasbegi (Busturia)
24. Mundaka
25. Bermeo

- The reverse direction is on the same PDF.
- E1 and E4 share the Lemoa–Matiko trunk (13 stops).
- `Amorebieta Geralekua` (E4 header) and `Amorebieta Geltokia` (E1) are different names; the E4 PDF note also mentions a train change at `Amorebieta Geltokia`. This needs confirmation.
- Destination variant: the 22:12 train reaches Bermeo on Saturdays and only Gernika on Sundays/holidays.
- Source: `E4_Bilbao-Bermeo_Bilbao_CARTEL_50x70_INVIERNO_2026_2.pdf`, page 1.

## Cross-line reconciliation

- **Shared Bilbao core**: Matiko-Bilbao, Uribarri, Zazpikaleak/Casco Viejo, Zurbaranbarri, Txurdinaga, Otxarkoaga and Kukullaga-Etxebarri are shared by E1, E3/L3 and E4.
- **E1/E4 shared trunk**: Lemoa–Matiko. E1 uses `Amorebieta Geltokia`; E4 uses `Amorebieta Geralekua`.
- **E1/E2 shared Donostia section**: Pasaia–Errekalde on the E1 through service.
- **Similar names that are distinct stops**: `Amorebieta Geltokia` vs `Amorebieta Geralekua`; `Eibar`, `Azitain`, `Ardantza`, `Amaña`, `Unibertsitatea`; `Lurgorri`, `Gernika`, `Institutua`; `S. Kristobal`, `Axpe`, `Itsasbegi`.
- **Direction-specific naming**: only the Amara variants differ; merged to `Amara Donostia`.

## Resolved identity questions

1. **Amorebieta Geltokia vs Amorebieta Geralekua** — distinct stops on distinct lines: Geltokia on Bilbao–Donostia (E1), Geralekua on Bilbao–Bermeo (E4).
2. **Does E3 call at Matiko?** Yes — the stop is `Matiko-Bilbao`.

## Deferred to the extraction-rules ticket

- Do all E3 services call at Ola (Sondika), or only some?
- Is Gaintxurizketa conditional on all E2 services, or only the 30-minute pattern?

## Source coordinates

- E1: the coordinate grid is in `../prototypes/e1-weekday-parser/parse_e1.py` (`FULL_42`) and the prototype README.
- E2/T1 and E4: header x-coordinates are in `01-stop-headers.json`.
- E3/L3: the PDF header text is fragmented; the names above come from the page-1 diagram, not a reliable text layer.
