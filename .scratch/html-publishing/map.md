# Publish the timetables as HTML on GitHub Pages

Status: charted — 3 decision tickets on the frontier, spec task blocked.

## Destination

A written specification for a generated HTML view of the timetables — index, per-line/direction/calendar pages and a searchable Master — plus a GitHub Pages build-and-deploy pipeline. Implementation is a separate effort.

## Notes

- **Effort type**: planning. The map resolves decisions; it does not build the site or deploy it.
- **Issue tracker**: local markdown. This file is the map; tickets live in `issues/`. See `docs/agents/issue-tracker.md`.
- **Data source**: the existing normalized `Service` model and corridor definitions, not the generated `.xlsx`. The service ordering contract is [the service sorting specification](../../.scratch/service-sorting/spec.md).
- **Current automation**: `.github/workflows/tests.yml` already downloads the six PDFs, runs the tests and rebuilds the workbook on push/PR/manual dispatch. It has no Pages permissions or deploy job, and the repo has no GitHub remote/Pages setup yet.
- **Glossary**: [GLOSSARY.md](../../GLOSSARY.md), especially Service, Calendar, Service day, Service order and Wide timetable.

### Standing decisions (settled during charting)

1. The destination is a **specification first**; the implementation is a separate effort.
2. Architecture: **hybrid** — static pre-rendered pages for direct links, plus client-side filtering/search on the Master.
3. Generator: **Python + Jinja2**, reusing the `Service` model; no Node toolchain.
4. Views: **index + per-line/direction/calendar pages + a searchable Master**.
5. Publishing scope: **HTML + `services.json` + the Excel workbook download**; the source PDFs are not republished.
6. Automation: **one workflow** with `test` and `deploy` jobs; deploy only on `main`, using the GitHub Pages actions.
7. Language: **Basque primary**, bilingual Basque/Spanish interface labels, Basque-only stop names.
8. Tables: **wide timetable with sticky headers/stop names and horizontal scrolling**; no mobile card view in the first version.

## Decisions so far

- [Decide the HTML site structure and URL scheme](issues/01-site-structure.md): static views with stable slugs; index, per-line/direction/calendar pages, Master, JSON and workbook download, all linked relatively.
- [Decide the `services.json` data contract](issues/02-data-contract.md): one versioned `services.json` with meta, lines, calendars, stops, corridors and canonically ordered services with stop times; no PDFs or internal evidence.

## Not yet specified

- The Jinja2 template decomposition and partial naming.
- Whether frequency rules, provenance and source notes get their own views.
- Whether to include a language switcher, an accessibility statement or both.
- Whether to expose a site-wide search index or SEO metadata beyond `services.json`.
- Whether the site needs a favicon or brand asset set beyond the CSS palette.
- How much of the build version and generated timestamp to surface on every page.

## Out of scope

- Implementing the generator or the Pages workflow; the destination is the spec.
- Creating the GitHub remote, enabling Pages or pushing the branch; those are implementation/prerequisite steps.
- Republishing the source PDFs.
- A mobile card view for the first version.
- Server-side search, a backend or a database.
- User accounts, personalization or saved journeys.
- Real-time data, live APIs or disruption feeds.
- Native mobile apps.
- Spanish stop-name aliases.
- Replacing the Excel workbook; HTML is an additional view.
- Publishing the internal `Validation`, `Frequency rules` or `Manifest` evidence as HTML.
- PDF generation as a deliverable; print CSS can be specified, but PDF output is out of scope.
