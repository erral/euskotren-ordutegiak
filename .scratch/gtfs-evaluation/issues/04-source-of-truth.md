# Decide the timetable source of truth and refresh policy

Type: grilling
Status: resolved
Parent: [Evaluate Euskotren GTFS as a timetable source](../map.md)

## Question

Given the research, which model should the static pipeline adopt?

- **(a) GTFS as the static source of truth**, with the PDF-derived output kept only as a validation/provenance and last-known-good fallback.
- **(b) PDFs as the primary source**, with GTFS used as a cross-check or diff alert.
- **(c) Both as independent sources**, with a diff/alert and no single source of truth.
- **(d) Keep PDFs for the published workbook/HTML**, and use GTFS only for a future real-time feature.

Also decide:

- the refresh cadence (daily or weekly) and what happens when the GTFS window ends or the feed is unavailable;
- whether "PDF fallback" means publishing the last known good GTFS build, publishing the PDF-derived build, or failing the deployment;
- whether the workbook and HTML must stay byte-for-byte compatible with the current output, or may gain GTFS-derived improvements.

➡️ Recommendation: **(a)**. Adopt GTFS as the static source of truth; keep the PDF-derived output as a diff/validation artifact and last-known-good fallback; rebuild daily with a staleness alarm; allow GTFS-derived improvements such as arrival/departure times and date-specific calendars after the first migration.

## Answer

Resolved 2026-11-25. Option **(a)** accepted.

- **Source of truth**: the static Euskotren GTFS feed.
- **PDFs**: retained as a validation/provenance artifact and reference build, not as the primary parser.
- **Refresh**: rebuild from GTFS daily; alarm or fail when the feed is unavailable or its validity window is stale. A stale GTFS build must not be published; keep the last successful build live.
- **First migration**: preserve the current workbook and wide HTML timetable shapes. GTFS-derived improvements such as arrival/departure times and date-specific calendars are follow-ups.
- **Real-time**: out of scope for the static pipeline. GTFS-RT trip updates may be evaluated later as a live-service feature.

The exact publish-on-failure behaviour (keep last successful deployment vs publish the PDF-derived reference build) remains an implementation detail for the follow-up effort.

## Comments

- Charted 2026-11-25 from the three research tickets.
- 2026-11-25: claimed and resolved. The user chose option (a), GTFS as the static source of truth.
