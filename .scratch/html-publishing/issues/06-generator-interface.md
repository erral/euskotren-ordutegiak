# Decide the generator interface and build integration

Type: grilling
Status: open
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

How should the HTML generator fit into the Python package and the build?

Cover: module name, public entry point, CLI subcommand, output directory, Jinja2 template location, whether `all` includes the site, reuse of `Service`, `CORRIDORS` and the service-order keys, and whether the xlsx or the in-memory services are the input.

➡️ Recommendation: `euskotren_timetable/site.py` with a `build_site(services, output_dir, manifest)` entry point; a `build-html` CLI subcommand (also included in `all`); output `output/html/`; templates under `euskotren_timetable/templates/`; in-memory `Service` input; reuse the existing corridors and sort keys. Add Jinja2 as a project dependency.

## Comments

- Charted 2026-11-21. Waiting for the generator-interface decision.
