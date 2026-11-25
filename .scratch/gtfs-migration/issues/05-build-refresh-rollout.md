# Decide build, refresh and rollout

Type: grilling
Status: open
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

## Comments

- Charted 2026-11-25.
- 2026-11-25: licence confirmed as CC BY 4.0 in [Confirm Open Data Euskadi licence and attribution](06-license-attribution.md); the attribution and change-notice requirements are settled for this ticket.
- 2026-11-25: [Decide validation and the PDF-diff contract](04-validation-pdf-diff.md) resolved; all blockers are clear and this ticket is now on the frontier.
