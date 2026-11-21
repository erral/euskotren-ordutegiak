# Decide how the generated site is validated

Type: grilling
Status: resolved
Blocked by: 03, 05, 06
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What checks must the generated site pass before it is deployed?

Cover: JSON schema/serialization tests, HTML generation and page-count tests, canonical service order, required links and anchors, a link checker, excluding PDFs from the artifact, accessibility checks, and where these run in the workflow.

➡️ Recommendation: unit tests for the JSON contract and page generation; a crawl of the generated `output/html` for broken internal links; assertions that the service order matches the existing contract; an artifact check that no PDFs are present; and a Ruff/test/link-check gate before deploy. No Lighthouse or axe gate in the first version.

## Answer

Resolved 2026-11-21. Both recommendations accepted.

- **Validation layers**: JSON contract tests; HTML page-generation tests; canonical service order; required links and `#service-id` anchors; a crawl of `output/html` for broken internal links; an artifact check that no PDFs are present; Ruff and the unit suite.
- **Gate**: the `test` job runs all checks; `deploy` needs `test`; any failure blocks publishing.
- **First version**: no Lighthouse or axe accessibility gate.

## Comments

- Charted 2026-11-21. Blocked by the page-content, deployment and generator-interface tickets.
- 2026-11-21: claimed for resolution; all blockers resolved.
- 2026-11-21: answered “ok” to both.
