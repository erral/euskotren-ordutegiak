# Assess GTFS licensing, URL stability and operating constraints

Type: research
Status: resolved
Parent: [Evaluate Euskotren GTFS as a timetable source](../map.md)

## Question

What licence and attribution terms apply to the GTFS, how stable are the URLs and update cadence, and what operational constraints does a GTFS-first pipeline inherit?

## Answer

Resolved 2026-11-25.

- The index is a stable pointer; the GTFS URL redirects to a versioned S3 object with `ETag`, `Last-Modified` and `x-amz-version-id`.
- Static GTFS is published daily around 07:00 Europe/Madrid; the index is refreshed during the day.
- The static feed window is 2026-11-25 → 2026-12-30. A build must refresh on a schedule (at least weekly, preferably daily) and alarm when the window is stale.
- `attributions.txt` credits Eusko Trenbideak but does not state a licence; `feed_info.txt` gives the publisher and contact but no licence. The Open Data Euskadi redistribution terms need confirmation before publishing GTFS-derived data.
- GTFS-RT trip updates are live; vehicle positions/alerts are empty at the sample time. NeTEx/SIRI return a BIG-IP logout page and are unavailable until access is resolved.
- Risks: feed expiry, licence clarity, blocked XML feeds, calendar drift, feed scope, stop aliases.

See [research/03-license-operations.md](../research/03-license-operations.md).

## Comments

- Charted 2026-11-25 from response headers and feed metadata.
