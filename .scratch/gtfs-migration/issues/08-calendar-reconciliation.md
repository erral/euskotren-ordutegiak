# Decide GTFS-to-published calendar reconciliation

Type: grilling
Status: resolved
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

The implementation spike found that the GTFS feed and the current PDF-derived output are not the same timetable edition or calendar grouping. How should the first GTFS publication reconcile them?

Evidence from the live 2026-11-25 feed:

- **In-scope GTFS rail trips:** 2,186 (E3a excluded) against **2,225 PDF service rows** — 39 fewer.
- **Unique timetable patterns:** 913 GTFS patterns against **1,521 PDF patterns** — 608 fewer.
- Our date-derived calendar expansion produced 2,845 *calendar candidates*; that is the same GTFS trip emitted into several calendars, not more physical services.
- Only **599 unique patterns** are common; 922 PDF patterns have no GTFS match and 314 GTFS patterns have no PDF match.
- Seven public-ID conflicts, for example two variants at `E1-PASAIA-MATIKO-WE-0735`, `E3-L3-LEZAMA-KUKULLAGA-WD-2252` and `E4-MATIKO-BERMEO-WE-2212`.
- The E1 weekend GTFS trips omit **Arroa** entirely, while the PDF weekend table publishes Arroa at 08:33.
- The PDF calendars are source-table groups, not pure day types: E1/E2 have SA/SU/WE overlap, E3-L3 has WE but no SA/SU, and E4 has a 22:12 SU variant and a 22:12 SN special.

Options:

- **(a) GTFS as the new truth**: publish the GTFS-derived timetable, use the PDF diff as a review report during the one-week `/` vs `/gtfs/` preview, and keep a hard **integrity** gate (unmapped stops, duplicate IDs, stale feed) rather than a hard equality gate. Add a suffix for same-departure variants. Keep representative-day calendars for the first cut and defer date-aware calendars.
- **(b) PDF-assisted reconciliation**: use the PDF reference to assign each GTFS service its published calendar and public ID; GTFS supplies the times. Preserve the current output and the hard equality gate, at the cost of keeping the PDFs as a grouping oracle.
- **(c) Curated overrides**: keep the GTFS date-derived calendars, add explicit overrides for the known conflicts and special services.
- **(d) Pause**: investigate the timetable differences before choosing.

➡️ Recommendation: **(a)**. The whole point of the move is that GTFS is fresher; forcing equality with the PDF output would hide the very changes we are trying to publish. Use the one-week preview as the human review, keep the integrity gate hard, and treat the PDF diff as a review report.

## Answer

Resolved 2026-11-25. The chosen model is **parallel publication, not reconciliation**:

- `/` remains the PDF-derived site.
- `/gtfs/` is the GTFS-derived site.
- `/compare.html` is a side-by-side comparator showing both tables, service/departure counts, PDF-only, GTFS-only and changed departures, with links into both sites.
- No attempt is made to merge the two editions. The comparator and its note state that the PDF and GTFS editions differ and that differences are expected.
- Same-departure collisions get a deterministic numeric suffix only for the colliding service IDs.
- Representative-day calendars are used for the first GTFS view; date-aware calendars remain a follow-up.
- The hard PDF equality gate is replaced by an **integrity gate** (unmapped stops, duplicate IDs, stale feed) plus the comparator as the review mechanism.

## Comments

- Charted 2026-11-25 from the three research tickets.
- 2026-11-25: found while implementing the GTFS adapter on `feat/gtfs-migration`.
- The adapter, 82-stop alias table and provenance fields are now wired into `build-html --source gtfs`; `/gtfs/` and `/compare.html` are generated.
- 2026-11-25: claimed and resolved. The user chose parallel publication with a comparator: PDF at `/`, GTFS at `/gtfs`, no reconciliation; note the differences.
