# Euskotren ordutegiak

One normalized Euskotren winter-2026 timetable, generated from the official PDFs and published as:

- a canonical **Excel workbook**;
- a static, searchable **HTML site**.

Basque is the primary language; interface labels are bilingual Basque/Spanish. Stop names are Basque-only; Spanish aliases are intentionally omitted.

The workbook is the source of truth. The HTML site is an additional view built from the same parsed `Service` data and the same ordering contract.

## Features

### Timetable data

- **2,227 services** on **E1, E2-T1, E4 and E3-L3**, both directions.
- **Calendars:** weekday, Saturday, Sunday/holiday, combined weekend, Friday night and Saturday night.
- Through-running and cross-line membership: a service appears in every corridor it traverses, such as E1 services on the shared E2-T1 Donostia section.
- Partial and special services: E1 Pasaia–Zumaia, Zaldibar–Matiko/Traña, Elgoibar–Matiko and Eibar–Ermua; E2 Añorga shuttles; E4 Gernika variants and short-turns; the Amorebieta Geltokia transfer column; and the night blocks.
- Canonical ordering shared by Excel and HTML: **calendar → departure → line → direction → service ID**. Corridor pages put the corridor’s own line first when services share a departure.
- **212 structural validation checks** and **163 unit tests**.

### Excel workbook

`output/euskotren_timetables_winter_2026_v12.xlsx` contains 17 sheets:

- `README`, `Stops`, `Calendars`, `Manifest`, `Coverage` and `Source notes`;
- `Master` with one canonical row per service;
- eight corridor sheets with services as rows and stops as columns;
- `Frequency rules` with compressed source rules and expanded services;
- `Validation` with the structural checks for the run.

Calendar blocks are stacked in each corridor sheet. The `Coverage` sheet marks every line/calendar pattern as `Included` or `Pending`. `Source notes` keeps the verbatim Basque/Spanish notes from the posters.

### HTML site

`make html` writes `output/html/` with:

- an index with line, direction and calendar links, validity and downloads;
- one page for every non-empty line/direction/calendar combination;
- a calendar switcher, sticky table header and horizontal scrolling; the first column scrolls with the table;
- a stop search filter with datalist suggestions, accent-insensitive matching, service row filtering and matching-column highlighting;
- a metadata toggle for Service ID, line, pattern, origin, destination, departure and arrival;
- a Master page with text search and line, calendar, origin, destination and departure filters;
- `data/services.json` (schema version 1) and the workbook download;
- print styles, a skip link, keyboard-accessible scroll regions and `aria-live` result counts;
- relative links, so the site works from a project Pages URL;
- no source PDFs in the published artifact.

### Automation

- GitHub Actions runs Ruff, the full test suite, the workbook/site build and the site validation gate.
- The `deploy` job publishes `output/html` to GitHub Pages only from `main`.

## Quick start

Requirements: **Python 3.12+** and **Poppler** (`pdftotext`).

```bash
python3 -m pip install -e ".[dev]"
python3 -m euskotren_timetable.cli all
```

`all` downloads the official PDFs, builds the workbook and builds the HTML site.

Or use Make:

```bash
make workbook   # Excel workbook only
make html       # workbook + static site in output/html
```

`make workbook` and `make html` expect the source PDFs in `data/pdfs/`. Run the manifest command first on a fresh checkout.

### Individual commands

```bash
python3 -m euskotren_timetable.cli manifest
python3 -m euskotren_timetable.cli build-weekday
python3 -m euskotren_timetable.cli build-html
python3 -m euskotren_timetable.cli validate-site --output output/html
```

### Outputs

- `output/euskotren_timetables_winter_2026_v12.xlsx`
- `output/html/` — the static timetable site
- `output/validation.md`
- `data/manifest.json`
- `data/pdfs/*.pdf`

## Publishing to GitHub Pages

The repository is intended to be named **`euskotren-ordutegiak`**, so the site will be served at:

`https://<owner>.github.io/euskotren-ordutegiak/`

After creating the repository:

1. Push `main`.
2. Open **Settings → Pages**.
3. Set **Source** to **GitHub Actions**.

The workflow runs the tests, builds and validates the site, and deploys `output/html`. If validation fails, deployment is blocked.

## Tests, linting and validation

```bash
make test
make lint
python3 -m euskotren_timetable.cli validate-site --output output/html
```

The site validation checks internal links and anchors, duplicate IDs, the JSON payload and the absence of PDFs in `output/html`. The test suite covers the timetable parsers, ordering, workbook contracts and the generated site.

## Layout

| Path | Purpose |
|---|---|
| `euskotren_timetable/cli.py` | CLI, build orchestration and manifest workflow |
| `euskotren_timetable/parse_*.py` | Coordinate-based PDF table parsers |
| `euskotren_timetable/corridors.py` | Eight corridor definitions and cross-line membership |
| `euskotren_timetable/model.py` | Normalized `Service` / `StopTime` records |
| `euskotren_timetable/service_order.py` | Shared canonical sort contract |
| `euskotren_timetable/validate.py` | 212 structural checks |
| `euskotren_timetable/workbook.py` | Excel renderer |
| `euskotren_timetable/site.py` | Static HTML generator and link validator |
| `euskotren_timetable/templates/` | Jinja2 site templates |
| `euskotren_timetable/assets/` | Site stylesheet and Master/stop-filter scripts |
| `euskotren_timetable/manifest.py`, `pdf.py` | PDF download, provenance and extraction |
| `euskotren_timetable/stops.py`, `source_notes.py` | Canonical stops and poster notes |
| `data/manifest.json`, `data/corrections.yaml` | Source URLs and sidecar corrections |
| `tests/` | Unit and generated-site tests |

## Legend

- Blank cell = does not stop.
- `?` = time not published in the source; shown in red on the HTML site.
- `>` = the train passes without stopping.
- Times are 24-hour. After-midnight times use `24:xx`/`25:xx`; a 00:30 Sunday train belongs to Saturday night.
- `FN` = Friday night and holiday eves; `SN` = Saturday night.

## Source

Timetable data is derived from the official Euskotren winter-2026 PDFs. The source manifest records each URL and SHA-256 hash.

## Disclaimer

This is an unofficial project and is not affiliated with Euskotren. Always check the official Euskotren timetable before travelling.

The project was built with [OpenCode](https://opencode.ai) using [Matt Pocock’s skills](https://github.com/mattpocock/skills) and [DeepSeek Flash 4-flash](https://www.deepseek.com/).

## License

GPL-2.0. See [LICENSE](LICENSE).
