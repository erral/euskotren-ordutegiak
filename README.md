# Euskotren single timetable

Build one Excel workbook from the official Euskotren winter-2026 timetable PDFs.

The planning map and implementation spec live in `.scratch/euskotren-timetable/`:

- [Map](.scratch/euskotren-timetable/map.md)
- [Implementation spec](.scratch/euskotren-timetable/spec.md)
- [Stop inventory](.scratch/euskotren-timetable/research/01-stop-inventory.md)
- [E1 weekday prototype](.scratch/euskotren-timetable/prototypes/e1-weekday-parser/README.md)

## Current slice

The production slice covers:

- **E1, E2/T1, E4 and E3/L3 weekdays in both directions**;
- **E1, E2/T1, E4, E3 and L3 combined weekend (Saturday + Sunday + holiday), both directions**;
- **E2/T1 Saturday and Sunday/holiday Añorga shuttle, both directions**;
- **E1, E2/T1 and E4 Saturday night, both directions** (after-midnight times as `24:xx`/`25:xx`);
- **E3-L3 Friday night and Saturday night**, including the E3 Lezama branch Saturday night.

It downloads the current PDFs, parses the tables by word coordinates, expands the E1 hourly, E2 30-minute, 15-minute and 7.5-minute shuttle, E4 30/60-minute, E3 15/30-minute and L3 7.5/10-minute rules, and builds corridor views where a service appears in every corridor it traverses. Weekday and weekend services are stacked as separate calendar blocks in the same corridor sheets; the E2 Saturday and Sunday/holiday shuttles use their own `SA`/`SU` blocks.

The workbook's `Coverage` sheet lists every line/calendar pattern and marks it `Included` or `Pending`.

The E2 weekend **full-line and separate Saturday/Sunday Añorga shuttle** are included. The E1 Topo stops omitted from the 42-column full-line tables are merged from the `Pasaia → Zumaia` / `Zumaia → Pasaia` partial tables, using the poster side note that every train stops between Pasaia and Aia-Orio. The **E1, E2/T1, E4 Saturday-night** and **E3-L3 Friday/Saturday-night** blocks are included; after-midnight times are stored as `24:xx`/`25:xx` with a day offset. The E4 22:12 Saturday Bermeo special is part of the night block, the 22:12 Sunday/holiday Gernika variant is a separate `SU` service, and the 22:52/22:45 Gernika short-turns are part of the weekend block. The **Pasaia–Zumaia / Zumaia–Pasaia short-turns** are included for weekdays, Saturdays and Sundays, along with the **Zaldibar→Matiko**, **Matiko→Traña**, **Elgoibar↔Matiko** and **Eibar↔Ermua** partials. The E1 refuerzo tables are complete. The E4 Gernika short-turns and the Amorebieta Geltokia transfer column are included. Spanish aliases are intentionally omitted; Basque names remain canonical.

The workbook's `Source notes` sheet keeps the verbatim Basque/Spanish side notes from the posters.

## Run

```bash
python3 -m euskotren_timetable.cli all
```

Outputs:

- `output/euskotren_timetables_winter_2026_v12.xlsx`
- `output/html/` — the static timetable site
- `output/validation.md`
- `data/manifest.json`
- `data/pdfs/*.pdf`

Individual steps:

```bash
python3 -m euskotren_timetable.cli manifest
python3 -m euskotren_timetable.cli build-weekday
python3 -m euskotren_timetable.cli build-html
python3 -m euskotren_timetable.cli validate-site --output output/html
```

## HTML site

`build-html` builds the workbook and the static site. The site contains the index, per-line/direction/calendar pages, the searchable Master, `data/services.json` and a workbook download under `output/html/downloads/`.

The GitHub Actions workflow runs the tests, builds and validates the site, and deploys `output/html` to GitHub Pages from `main`. The repository must have **Settings → Pages → Source: GitHub Actions** enabled once.

## Tests

```bash
python3 -m unittest discover -s tests
```

## Formatting and linting

Ruff is the formatter and linter; its configuration lives in `pyproject.toml`.

```bash
python3 -m pip install -e ".[dev]"
make format   # ruff format . && ruff check --fix .
make lint     # ruff format --check . && ruff check .
```

The GitHub Actions workflow runs `make lint` (equivalently, both Ruff checks) before the tests.

## Layout

- `euskotren_timetable/stops.py` — canonical stops and shared trunks.
- `euskotren_timetable/corridors.py` — eight corridors and cross-line membership.
- `euskotren_timetable/pdf.py` — coordinate-based PDF extraction.
- `euskotren_timetable/parse_e1.py` — E1 Pasaia → Matiko weekday.
- `euskotren_timetable/parse_e1_reverse.py` — E1 Matiko → Pasaia weekday full-line.
- `euskotren_timetable/parse_e1_weekend.py` — E1 combined weekend full-line.
- `euskotren_timetable/parse_e1_night.py` — E1 Saturday-night Deba↔Matiko blocks.
- `euskotren_timetable/parse_night.py` — shared E2/T1 and E4 Saturday-night tables.
- `euskotren_timetable/parse_e1_partial.py` — E1 Pasaia↔Zumaia partial tables and Topo merge.
- `euskotren_timetable/source_notes.py` — verbatim poster side notes.
- `euskotren_timetable/parse_e2.py` — E2/T1 full-line and shuttle weekdays.
- `euskotren_timetable/parse_e2_weekend.py` — E2/T1 combined weekend full-line.
- `euskotren_timetable/parse_e2_shuttle_weekend.py` — E2/T1 Saturday and Sunday/holiday Añorga shuttle.
- `euskotren_timetable/parse_e3.py` — E3 Lezama branch weekdays and weekend.
- `euskotren_timetable/parse_e4.py` — E4 full-line weekdays and weekend.
- `euskotren_timetable/parse_l3.py` — L3 Matiko ↔ Kukullaga local weekdays and weekend.
- `euskotren_timetable/parse_l3_night.py` — E3-L3 Friday/Saturday night blocks.
- `euskotren_timetable/model.py` — normalized records.
- `euskotren_timetable/validate.py` — structural checks.
- `euskotren_timetable/workbook.py` — Excel renderer with stacked calendar blocks.
- `euskotren_timetable/site.py` — static HTML site generator and link validator.
- `euskotren_timetable/templates/` — Jinja2 templates for the site.
- `euskotren_timetable/assets/` — site stylesheet and Master filter script.
- `euskotren_timetable/manifest.py` — PDF download and provenance.
- `data/corrections.yaml` — sidecar corrections, applied on regeneration.

## Legend

- Blank cell = does not stop.
- `?` = time not published in the source.
- Times are 24-hour.
