# Decide the GitHub Pages deployment contract

Type: grilling
Status: open
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

How should the generated site be built and deployed to GitHub Pages?

Cover: one workflow or two; which jobs run; deploy trigger; permissions; environment; Pages actions and versions; artifact directory; whether the source PDFs are excluded; base path; `.nojekyll`; and whether a custom domain is in the first version.

➡️ Recommendation: one workflow with `test` and `deploy` jobs, deploy only on `main`, `contents: read` + `pages: write` + `id-token: write`, `github-pages` environment, `actions/configure-pages@v5` + `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`, artifact `output/html`, and no PDFs. No custom domain in the first version.

## Comments

- Charted 2026-11-21. Waiting for the deployment-contract decision.
