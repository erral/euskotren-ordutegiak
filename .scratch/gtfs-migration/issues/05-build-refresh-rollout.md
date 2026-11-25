# Decide build, refresh and rollout

Type: grilling
Status: resolved
Blocked by: 01, 02, 03, 04
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

How should the GTFS pipeline be integrated, refreshed and rolled out?

Cover at least:

- **CLI**: add a `--source gtfs|pdf` switch or a new build command; define the staged default.
- **Manifest**: download the GTFS zip and record its SHA-256, `feed_version`, `feed_start_date` and `feed_end_date` in a GTFS manifest; carry that provenance into `data/services.json` and the site metadata.
- **Workflow**: a daily schedule that downloads the feed, checks the validity window, builds, runs the PDF diff and deploys only on success; keep the last successful deployment when a run fails.
- **Staleness**: fail when the feed is missing, the download fails, or `feed_end_date` is too close.
- **Attribution**: add the confirmed CC BY 4.0 attribution text, source/licence links and change notice to the README and site footer.
- **Rollout**: dual-run and compare before cutover; keep the PDF parser as a validation tool and reference build.

➡️ Recommendation: a temporary `--source` switch, a versioned GTFS manifest with checksums, a daily scheduled build with a staleness gate and hard PDF diff, deploy only on success, and a dual-run cutover.

## Answer

Resolved 2026-11-25. All recommendations accepted, with a one-week parallel publication added to the rollout.

- **CLI**: add `--source gtfs|pdf` to `build-html` (with a `--gtfs` feed path). Start with `pdf` as the default, use `gtfs` for the CI build and diff, and flip the default to `gtfs` only at cutover. Keep the PDF path available as the validation/reference build.
- **Manifest**: generate a GTFS manifest in the build artifact with the source URL, SHA-256, `feed_version`, `feed_start_date`, `feed_end_date` and fetch time. Carry the feed version/window into `data/services.json` meta, the site metadata and the workbook metadata. Do not commit a new manifest daily; keep a committed schema/example and let the deployed artifact be the record.
- **Workflow**: extend the existing GitHub workflow with a daily scheduled run after the feed’s ~07:00 local publication. It downloads GTFS, checks the window, builds, runs the hard PDF diff and updates the published preview only on success. A failed run leaves the last successful deployment live. The push/PR/manual test job and the PDF download remain.
- **Staleness**: fail when the feed is missing, the download fails, or fewer than **7 days** remain in `feed_end_date`.
- **Publication model**: for **one week**, publish both variants from the same GitHub Pages site:
  - `/` stays the current PDF-derived site;
  - `/gtfs/` is the GTFS preview, linked from the main page with a visible “GTFS preview” banner/label;
  - both workbook variants are published with distinct names (`…_pdf.xlsx` and `…_gtfs.xlsx`);
  - the daily workflow updates the preview only when the hard diff passes.
  After one week of clean daily runs, GTFS moves to `/`, and the PDF build is retired from the public site but kept as the CI validation/reference build.
- **Attribution**: at cutover add the CC BY 4.0 attribution to the README, site footer and workbook metadata: credit Eusko Trenbideak, link the source and licence, note changes and the feed version. Derived outputs are published under CC BY 4.0; the code stays GPL-2.0.

## Comments

- Charted 2026-11-25.
- 2026-11-25: licence confirmed as CC BY 4.0 in [Confirm Open Data Euskadi licence and attribution](06-license-attribution.md); the attribution and change-notice requirements are settled for this ticket.
- 2026-11-25: [Decide validation and the PDF-diff contract](04-validation-pdf-diff.md) resolved; all blockers are clear and this ticket is now on the frontier.
- 2026-11-25: claimed and resolved. The user accepted all recommendations and added a one-week `/` (PDF) vs `/gtfs/` (GTFS) parallel publication before cutover.
