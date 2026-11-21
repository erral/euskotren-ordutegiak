# Write the HTML publishing specification

Type: task
Status: resolved
Blocked by: 01, 02, 03, 04, 05, 06, 07
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

Produce the destination artifact: `.scratch/html-publishing/spec.md`, the written specification for the HTML view and GitHub Pages pipeline.

It must cover:

- the site map and URL scheme;
- the `services.json` contract;
- the page content and table behaviour, including the Master search;
- the visual, responsive and accessibility rules;
- the generator interface and build integration;
- the GitHub Pages workflow and permissions;
- the validation and deployment gate;
- concrete examples from the current workbook and service-order contract;
- an explicit implementation boundary: this spec changes no generator code and does not create the GitHub remote or Pages site.

Resolved when the spec is written and reviewed. The task is AFK to draft and HITL to review.

## Answer

Resolved 2026-11-21.

The specification is written at [`spec.md`](../spec.md). It defines:

- the site map, URL scheme and relative-link rules;
- the versioned `services.json` contract;
- the index, corridor and Master page contracts, including cell states and the night legend;
- the custom CSS, responsive and accessibility rules;
- the `site.py` / `build_site` generator, `build-html` CLI and packaged Jinja2 templates;
- the single `test` + `deploy` Pages workflow and permissions;
- the validation and deployment gate;
- first-version defaults for the remaining details;
- an explicit implementation boundary.

Reviewed and confirmed. Implementation and repository Pages setup remain separate steps.

## Comments

- Charted 2026-11-21. Blocked by the seven decision tickets.
- 2026-11-21: claimed; spec drafted at [`spec.md`](../spec.md). Awaiting review before resolution.
- 2026-11-21: reviewed and confirmed; resolved.
