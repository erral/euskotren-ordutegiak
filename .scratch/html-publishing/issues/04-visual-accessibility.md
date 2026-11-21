# Decide the visual, responsive and accessibility rules

Type: grilling
Status: resolved
Blocked by: 03
Parent: [Publish the timetables as HTML on GitHub Pages](../map.md)

## Question

What should the site look and feel like, and which accessibility rules are non-negotiable?

Cover: CSS approach (custom stylesheet or framework), Euskotren-inspired palette, typography, sticky headers and first columns, focus states, colour contrast, table semantics (`caption`, `scope`), keyboard behaviour, mobile horizontal scrolling, and print CSS.

➡️ Recommendation: a custom stylesheet with no framework, an Euskotren-inspired green/blue palette, WCAG AA contrast, semantic `<table>` markup with captions and scoped headers, sticky headers/first columns, and print styles. No card view in the first version.

## Answer

Resolved 2026-11-21. Both recommendations accepted.

- **Visual system**: custom CSS, no framework. Euskotren-inspired green/blue palette exposed as CSS variables, system font stack, dense timetable typography, no icon set. Basic print styles hide navigation/filters and repeat table headers.
- **Accessibility/responsive**: semantic `<table>` with `<caption>`, `scope="col"` and `scope="row"`, sticky header and first columns, visible keyboard focus, WCAG AA contrast, keyboard-accessible horizontal scrolling on narrow screens, and no card view in the first version.

## Comments

- Charted 2026-11-21. Blocked by the page-content decision.
- 2026-11-21: claimed for resolution; page content resolved.
- 2026-11-21: answered “ok” to both.
