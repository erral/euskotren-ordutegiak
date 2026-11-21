# Define the refresh and versioning workflow

Type: grilling
Status: resolved
Blocked by: 05

## Question

Decide how the workbook stays current across seasons:

- how to detect new or changed PDFs (manifest, checksums, link discovery);
- how to regenerate the workbook without losing manual corrections;
- how to record the source PDF, season, extraction date, valid_from and open valid_to in the output;
- how timetable versions supersede one another, including mid-season starts such as 7 September and 21 November 2026;
- rerun the validation checks and compare against the previous baseline (ticket 09);
- what is automated versus manually reviewed.

Output: a refresh workflow section for the spec.

## Answer

Resolved 2026-11-21.

### Change detection

- Maintain a manifest of PDF URLs plus SHA-256 checksums.
- A refresh run fetches the timetable page, extracts the current PDF links, compares checksums, and reports new/changed/removed files before parsing.
- The manifest is versioned with the workbook.

### Manual corrections

- Corrections live in a sidecar file (YAML or CSV) keyed by service ID and stop.
- The sidecar is applied after parsing on every regeneration.
- The workbook is generated output and is never hand-edited.
- Correction changes are reviewed and versioned with the workbook.

### Manifest and provenance

- Each workbook carries a `Manifest` sheet and `README` metadata: source PDF URL, checksum, fetch date, page count, season, `valid_from`, open `valid_to`, and generator version.
- The filename includes season and version: `euskotren_timetables_winter_2026_v1.xlsx`.
- The `Master` sheet records the source PDF and frequency rule for each service.

### Supersession

- The generator uses the latest valid PDF per line and direction as of the generation date.
- A mid-season start, such as 21 November, supersedes the earlier version, such as 7 September, for the affected sections.
- Older versions are archived, not merged.

### Automation and change report

- Fetch, checksum, parse, validate and render are automated.
- Manual review and sign-off remain human.
- Each refresh produces a change report: new/removed/changed services, new `?`, and count changes.
- The change report is reviewed before sign-off.

### Cadence

- On-demand refresh when the PDFs change; no scheduler or background watcher.
