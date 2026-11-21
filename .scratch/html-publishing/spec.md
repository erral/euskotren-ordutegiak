# HTML publishing specification

Status: written 2026-11-21. Implementation is a separate effort.

## Purpose

Define a generated HTML view of the timetable data and a GitHub Pages build-and-deploy pipeline. The HTML is a second presentation of the same normalized services as the Excel workbook; it does not replace the workbook or introduce a second data model.

## Scope

In scope:

- the site map and URL scheme;
- the `/data/services.json` contract;
- index, corridor and Master page content;
- visual, responsive and accessibility rules;
- the Python/Jinja2 generator interface;
- the GitHub Pages workflow;
- validation and deployment gating.

Out of scope is listed at the end.

## Site map and URLs

All links are relative, so the site works under `https://<owner>.github.io/<repo>/`.

| Path | Purpose |
|---|---|
| `/` | Index: validity, generated time, line/direction/calendar links, downloads |
| `/line/<line>/<direction>/<calendar>.html` | One timetable page |
| `/master.html` | Searchable service index |
| `/data/services.json` | Machine-readable data |
| `/downloads/euskotren_timetables_winter_2026.xlsx` | Workbook download |
| `/assets/site.css`, `/assets/site.js` | Presentation and Master filtering |

Slugs:

- lines: `e1`, `e2-t1`, `e4`, `e3-l3`
- directions: `pasaia-matiko`, `matiko-pasaia`, `hendaia-lasarte`, `lasarte-hendaia`, `matiko-bermeo`, `bermeo-matiko`, `lezama-kukullaga`, `kukullaga-lezama`
- calendars: `weekday`, `saturday`, `sunday-holiday`, `weekend`, `friday-night`, `saturday-night`

Only non-empty line/direction/calendar combinations get a page, and the index links only those combinations. Every service row has `id="<service-id>"`, so `/line/e1/pasaia-matiko/weekday.html#E1-PASAIA-MATIKO-WD-0535` is a stable deep link.

## Data contract

`/data/services.json` is one versioned file:

```json
{
  "schema_version": 1,
  "meta": {
    "season": "Winter 2026",
    "valid_from": "2026-11-21",
    "valid_to": null,
    "generated_at": "2026-11-21T00:00:00+00:00",
    "generator_version": "0.1.0",
    "source_manifest": [
      {
        "label": "e1_pasaia_matiko",
        "url": "https://www.euskotren.eus/...",
        "sha256": "..."
      }
    ]
  },
  "lines": [
    {
      "code": "E1",
      "slug": "e1",
      "name": "E1",
      "directions": [
        {"name": "Pasaia-Matiko", "slug": "pasaia-matiko"},
        {"name": "Matiko-Pasaia", "slug": "matiko-pasaia"}
      ]
    }
  ],
  "calendars": [
    {
      "id": "WD",
      "slug": "weekday",
      "label_eu": "Astegunak",
      "label_es": "Laborables",
      "order": 0
    }
  ],
  "stops": [
    {"stop_id": "S001", "name": "Pasaia", "lines": ["E1", "E2-T1"]}
  ],
  "corridors": [
    {
      "sheet": "E1 Pasaia-Matiko",
      "line": "E1",
      "direction": "Pasaia-Matiko",
      "slug": "pasaia-matiko",
      "stops": ["Pasaia", "Altza (Donostia)"]
    }
  ],
  "services": [
    {
      "service_id": "E1-PASAIA-MATIKO-WD-0535",
      "primary_line": "E1",
      "pattern": ["through"],
      "direction": "Pasaia-Matiko",
      "calendar": "WD",
      "origin": "Pasaia",
      "destination": "Matiko-Bilbao",
      "departure": "5:35",
      "arrival": "8:25",
      "appears_in": ["E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"],
      "frequency_rule_ids": ["E1-WD-0535-1935-60"],
      "notes": ["Hourly frequency E1-WD-0535-1935-60"],
      "stop_times": [
        {"stop_name": "Pasaia", "time": "5:35", "disposition": "stop", "day_offset": 0}
      ]
    }
  ]
}
```

- `schema_version` is an integer; increment it on breaking changes.
- `meta` carries season, validity, generated time, generator version and the source manifest (official URL and SHA-256).
- `lines`, `calendars`, `stops` and `corridors` are stable reference data; the corridor `stops` array is the display order.
- `services` is the canonical service order. Clients may rely on the array order.
- `pattern` is the service’s pattern list; `appears_in` uses corridor sheet names; `stop_times` follows the service calling pattern.
- The file excludes the source PDFs and the internal validation, frequency-rule and manifest evidence sheets.

## Page contracts

### Index

The index shows:

- the title, season and validity;
- the generated timestamp and generator version;
- a legend for `?`, `>`, blank and `24:xx`/`25:xx`;
- one section per line, with direction and available-calendar links;
- links to the Master, `services.json` and the workbook download;
- source attribution linking the official PDFs.

### Corridor page

One calendar per page. The header carries the line, direction and calendar, plus validity and generated time. A calendar switcher links the same line/direction to every available calendar, marking the current one with `aria-current="page"`.

The table:

- stops as columns, services as rows;
- metadata columns: **Service ID**, **Line**, **Pattern**, **Origin**, **Destination**, **Departure**, **Arrival**;
- metadata is **hidden by default** behind a “show metadata” toggle; the default reading view is stop times only;
- service notes available as a `title` tooltip on the service ID, not a full column;
- a table `<caption>` naming the line, direction and calendar;
- sticky header; horizontal scrolling in a keyboard-focusable container; the first column scrolls with the table;
- a stop search box that filters services to those serving the matching stop(s), highlights the matching stop columns and reports the visible count;
- a row `id="<service-id>"`;
- a `:target` highlight for deep-linked rows.

Cell states:

| State | Markup/display | Style |
|---|---|---|
| Stop | the time | normal, tabular numerals |
| Unpublished | `?` | red, bold |
| Pass | `>` | muted |
| Not served | blank | blank |

`FN` and `SN` pages add a legend for `24:xx`/`25:xx` and the service-day rule (“a 00:30 Sunday service belongs to Saturday night”).

The footer repeats validity, generated time, source links, the JSON link and the workbook download.

### Master

`/master.html` renders the full services table initially and filters it client-side. Columns:

**Service ID**, **Line**, **Direction**, **Calendar**, **Origin**, **Destination**, **Departure**, **Arrival**, **Pattern**, **Corridors**.

Filters:

- text search over service ID, origin and destination;
- line select;
- calendar select;
- origin select;
- destination select;
- departure-from and departure-to time inputs.

Filters are labelled and update a result count in an `aria-live="polite"` region. Without JavaScript the full table is still visible; the filter form is hidden or marked unavailable. No pagination or virtual scrolling in the first version.

## Visual, responsive and accessibility rules

- Custom CSS, no framework. Palette as CSS variables:

```css
:root {
  --brand-green: #7ab800;
  --brand-blue: #00519e;
  --ink: #1f2933;
  --muted: #5b6770;
  --surface: #ffffff;
  --surface-alt: #f3f6f4;
  --border: #cbd5d1;
  --danger: #b00020;
  --focus: #005fcc;
}
```

- System font stack; dense table typography; `font-variant-numeric: tabular-nums`.
- Sticky `thead th` with an opaque background; the first column scrolls with the table.
- Horizontal scroll container with `overflow-x: auto`, `tabindex="0"` and an accessible label.
- Visible `:focus-visible` outline; WCAG AA contrast; no animation or `prefers-reduced-motion` fallback needed.
- Semantic `<table>`, `<caption>`, `scope="col"` and `scope="row"`; skip link, `<header>`, `<nav>`, `<main>`, `<footer>`.
- `lang="eu"` on the document; Spanish interface labels are wrapped in `lang="es"` spans.
- Print styles hide navigation and filters, repeat table headers, and use A4 landscape with reasonable margins; no sticky positioning in print.
- No card view in the first version; narrow screens use horizontal scrolling.

## Generator and build integration

- New `euskotren_timetable/site.py` with `build_site(services, output_dir, manifest) -> Path`.
- Input is the in-memory `Service` list; no reading the generated workbook.
- Reuse `CORRIDORS`, `service_order.master_sort_key` and `service_order.corridor_sort_key` so HTML and Excel share the same order.
- Output directory: `output/html/`.
- Jinja2 templates under `euskotren_timetable/templates/`:
  - `base.html`, `index.html`, `corridor.html`, `master.html`;
  - partials for header, footer, filters, legend and table.
- Assets under `euskotren_timetable/assets/` (`site.css`, `site.js`).
- Add Jinja2 as a project dependency and package the templates/assets as package data.
- CLI: `build-html` with `--output` (default `output/html`) and `--manifest` (default `data/manifest.json`). `all` runs manifest + workbook + HTML.
- The generator writes `data/services.json`, copies the workbook to `downloads/euskotren_timetables_winter_2026.xlsx`, and builds only non-empty corridor/calendar pages.
- The site build is deterministic apart from `generated_at`; tests inject a fixed timestamp or compare structure, not the timestamp value.
- The generator must not mutate services, service IDs, stop order or the workbook.

## GitHub Pages deployment

A single workflow (extend `.github/workflows/tests.yml`):

- **`test` job** on push, pull request and manual dispatch:
  - checkout; Python 3.12; `poppler-utils`;
  - install `.[dev]`;
  - ruff format check and ruff check;
  - download the six PDFs from `data/manifest.json`;
  - run the unit suite;
  - build the workbook and the site;
  - run the site validation and artifact checks;
  - upload `output/html` with `actions/upload-pages-artifact@v3`.
- **`deploy` job**:
  - `needs: test`;
  - only on `main` and not on `pull_request`;
  - `environment: github-pages`;
  - permissions `contents: read`, `pages: write`, `id-token: write`;
  - `actions/deploy-pages@v4`.

Use `actions/configure-pages@v5` before the build, `.nojekyll` in the artifact, and a workflow-level `concurrency` group for Pages. No custom domain in the first version. The Pages source is “GitHub Actions” in the repository settings; that is a one-time repository setup, not part of the generator.

The artifact contains HTML, `data/services.json`, `assets/`, `downloads/<workbook>.xlsx` and `.nojekyll`; it contains no PDFs.

## Validation

Before deploy, the `test` job runs:

1. **JSON contract tests** — required keys, types, schema version, service count and canonical order.
2. **HTML generation tests** — index, Master and the expected non-empty corridor/calendar pages; required metadata and table structure.
3. **Order tests** — Master rows follow `master_sort_key`; corridor rows follow `corridor_sort_key`.
4. **Anchor/link tests** — every service row’s `id` is unique; every internal `href`/`src` resolves; every anchor target exists.
5. **Site crawl** — a small Python crawler over `output/html` reports broken internal links.
6. **Artifact check** — no `.pdf` files in `output/html`.
7. **Ruff and the unit suite** — the existing gate.

Any failure blocks `deploy`. No Lighthouse or axe gate in the first version; accessibility is checked by the semantic rules above and a manual review.

## Examples

- Canonical order at weekday `05:35`: in `Master`, `E1-PASAIA-MATIKO-WD-0535` before the E2-T1 service at the same time; in `E1 Pasaia-Matiko`, the E1 service first; in `E2-T1 Hendaia-Lasarte`, the E2-T1 service first.
- Night order: `23:45` before `24:00` before `25:37` in `SN`.
- Deep link: `/line/e1/matiko-pasaia/saturday-night.html#E1-MATIKO-PASAIA-SN-2345`.
- Cell states: a stop time, `?`, `>`, and a blank cell are visibly distinct.
- JSON: the `services` array is already in canonical order; the Master does not need to re-sort it before filtering.

## First-version defaults for open details

- No separate frequency-rule, provenance or source-note pages; those fields stay in `services.json` and tooltips.
- No language switcher or accessibility statement; bilingual labels are inline.
- Basic `<title>` and `<meta name="description">`; no sitemap or robots file.
- No favicon or brand asset set beyond the CSS palette.
- Footer shows generated timestamp, generator version, validity, source links, JSON and workbook links.
- Template decomposition is a starting point; implementation may split partials further.
- No Master pagination, virtual scrolling or card view.
- No custom domain.
- No PDF output or print-to-PDF deliverable; print CSS is included.

## Implementation boundary

This specification changes no generator code, templates or workflow. It also does not create the GitHub remote, enable Pages or push a branch. Those are implementation and repository-setup steps for the follow-up effort.

## Out of scope

- Implementing the generator or the Pages workflow.
- Creating the GitHub remote, enabling Pages or pushing the branch.
- Republishing the source PDFs.
- A mobile card view for the first version.
- Server-side search, a backend or a database.
- User accounts, personalization or saved journeys.
- Real-time data, live APIs or disruption feeds.
- Native mobile apps.
- Spanish stop-name aliases.
- Replacing the Excel workbook; HTML is an additional view.
- Publishing the internal `Validation`, `Frequency rules` or `Manifest` evidence as HTML.
- PDF generation as a deliverable.
