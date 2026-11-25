# GTFS licensing, URL stability and operating constraints

Evidence collected 2026-11-25.

## URL stability

- The canonical discovery file is the Moveuskadi `data-index.json`; its `last-update` was 2026-11-25 19:08:29.
- The GTFS URL in the index is:
  `https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip`
- It redirects to a versioned S3 object:
  `https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/euskotren/gtfs_euskotren.zip`
- The S3 response carries `ETag`, `Last-Modified` and `x-amz-version-id`, so a downloader can detect a changed feed without extra metadata.
- The index is the stable pointer; the per-feed URL is stable enough to fetch directly but should be taken from the index rather than hard-coded.

## Refresh cadence and horizon

- Static GTFS: built around 04:34 and published around 07:01 Europe/Madrid on 2026-11-25; `feed_version` encodes `20261125043408`.
- The index is refreshed during the day; the GTFS-RT/SIRI entries update every few minutes.
- The static feed's window is **2026-11-25 to 2026-12-30**. It is a rolling five-week feed, not a season-long document.
- Consequence: a static site/workbook built from GTFS must be rebuilt on a schedule (at least weekly, preferably daily) and must fail loudly when the feed window is stale or the feed fetch fails.
- The PDFs are season posters with an open `valid_to`; they are not refreshed daily but also do not expire on a five-week horizon.

## Licence and attribution

- `attributions.txt` credits **Eusko Trenbideak** as operator and points to `https://gardentasuna.euskotren.eus/eu`; it does not state a licence.
- `feed_info.txt` gives the publisher, contact and language but no explicit licence.
- The files are published on **Open Data Euskadi**, but the portal home page did not expose an obvious per-dataset licence in the fetched HTML.
- **Open risk**: confirm the Open Data Euskadi licence/attribution terms before redistributing GTFS-derived data in the workbook, HTML site or JSON.
- Current README already credits the official PDF sources; a GTFS-based pipeline would need equivalent attribution and a licence note.

## Real-time and XML access

- GTFS-RT trip updates work and are current (268 KB, last modified 2026-11-25 18:10 UTC).
- GTFS-RT vehicle positions and alerts were empty 15-byte FeedMessages at the sample time.
- NeTEx and all SIRI URLs return a 5,391-byte BIG-IP logout HTML page, both through the opendata URL and the direct S3 path, even with a browser User-Agent and referer.
- Consequence: NeTEx/SIRI cannot be evaluated as alternatives without resolving access. GTFS is the only immediately usable static format; GTFS-RT trip updates are the only immediately usable real-time feed.

## Operational risks

1. **Feed expiry** — the five-week window forces a scheduled rebuild and a staleness alarm.
2. **Licence clarity** — attribution is present, but redistribution terms are not stated in the feed.
3. **Blocked XML feeds** — NeTEx/SIRI access must be treated as unavailable until confirmed.
4. **Calendar drift** — date-specific service_ids/calendar_dates change with holidays; a cached build can silently become wrong if not refreshed.
5. **Feed scope** — the Euskotren GTFS includes trams, funicular and FCC; filtering and route mapping are required.
6. **Stop aliases** — GTFS names differ from the project's canonical names; a stale alias map can break joins.

## Conclusion

The GTFS is operationally usable and stable, but it is a rolling feed with a short horizon and unclear redistribution terms. A GTFS-first pipeline is feasible; it needs a scheduled refresh, a staleness check, a licence/attribution decision and an alias map.
