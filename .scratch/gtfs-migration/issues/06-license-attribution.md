# Confirm Open Data Euskadi licence and attribution

Type: research
Status: resolved
Parent: [Migrate the static timetable pipeline to Euskotren GTFS](../map.md)

## Question

What licence and attribution terms apply to the Euskotren GTFS, and what text/links must the workbook, HTML and JSON carry?

Cover at least:

- `attributions.txt` credits Eusko Trenbideak but states no licence; `feed_info.txt` gives the publisher and contact but no licence.
- Confirm the terms from the Open Data Euskadi portal, catalogue, API metadata or legal notice — not by assumption.
- Record the required attribution, any redistribution constraints, and whether the derived workbook/HTML/JSON may be published under the project's current licence.
- If the licence cannot be confirmed, say so and list exactly what is known and what is missing.

## Answer

Resolved 2026-11-25.

- **Licence**: the dataset is **CC BY 4.0** (Creative Commons Attribution 4.0 International). It is stated in the Open Data Euskadi catalogue record for the Moveuskadi dataset on the dataset card, in the DCAT RDF (`dct:license`), and in the page's schema.org JSON-LD. The GTFS zip itself has no licence file or field.
- **Redistribution**: allowed, including derivative works and commercial use. Required: credit the creator/publisher (Eusko Trenbideak / Basque Government), link to the source and to `https://creativecommons.org/licenses/by/4.0/`, indicate that changes were made, and cite the last-update date. No share-alike and no endorsement implication.
- **Recommended output licence**: publish the derived workbook/HTML/JSON under CC BY 4.0 with the attribution notice; keep the source code under GPL-2.0.
- **Caveats**: no dataset-specific prose licence page beyond the badge; the adjacent general legal-information link points at a different, all-rights-reserved notice; the Open Data notice has a legacy "do not alter" clause that sits awkwardly with CC BY 4.0. The specific, machine-readable CC BY 4.0 grant resolves these; attribution plus a change notice is the mitigation.
- **Attribution text will need to name Eusko Trenbideak, link to the GTFS source and CC BY 4.0, note the feed last-update/version, and state that times were transformed into the workbook/HTML views.**

See [research/license.md](../research/license.md).

## Comments

- Charted 2026-11-25.
- 2026-11-25: research subagent dispatched to write `research/license.md`.
- 2026-11-25: research complete; licence confirmed as CC BY 4.0 with the attribution/redistribution conditions recorded above.
