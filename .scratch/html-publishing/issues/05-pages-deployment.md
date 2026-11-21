# Decide the GitHub Pages deployment contract

Type: grilling
Status: resolved
Blocked by:
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

How should the generated site be built and deployed to GitHub Pages?

Cover: one workflow or two; which jobs run; deploy trigger; permissions; environment; Pages actions and versions; artifact directory; whether the source PDFs are excluded; base path; `.nojekyll`; and whether a custom domain is in the first version.

➡️ Recommendation: one workflow with `test` and `deploy` jobs, deploy only on `main`, `contents: read` + `pages: write` + `id-token: write`, `github-pages` environment, `actions/configure-pages@v5` + `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`, artifact `output/html`, and no PDFs. No custom domain in the first version.

## Answer

Resolved 2026-11-21. Both recommendations accepted.

- **Workflow**: one workflow with a `test` job (push/PR) and a `deploy` job that needs `test`, runs only on `main`, and consumes the Pages artifact built by `test`. No second workflow and no rebuild.
- **Artifact**: publish `output/html` containing HTML, `services.json` and the workbook; no source PDFs.
- **Permissions**: `contents: read`, `pages: write`, `id-token: write`; environment `github-pages`.
- **Actions**: `actions/configure-pages@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`; include `.nojekyll`.
- **First version**: no custom domain; relative links work under the project Pages path.

## Comments

- Charted 2026-11-21. Waiting for the deployment-contract decision.
- 2026-11-21: claimed for resolution.
- 2026-11-21: answered “ok” to both.
