# Decide how the generated site is validated

Type: grilling
Status: open
Blocked by: 03, 05, 06
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What checks must the generated site pass before it is deployed?

Cover: JSON schema/serialization tests, HTML generation and page-count tests, canonical service order, required links and anchors, a link checker, excluding PDFs from the artifact, accessibility checks, and where these run in the workflow.

➡️ Recommendation: unit tests for the JSON contract and page generation; a crawl of the generated `output/html` for broken internal links; assertions that the service order matches the existing contract; an artifact check that no PDFs are present; and a Ruff/test/link-check gate before deploy. No Lighthouse or axe gate in the first version.

## Comments

- Charted 2026-11-21. Blocked by the page-content, deployment and generator-interface tickets.
