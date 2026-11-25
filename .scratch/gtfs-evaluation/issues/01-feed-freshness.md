# Verify Euskotren feed freshness and access

Type: research
Status: resolved
Parent: [Evaluate Euskotren GTFS as a timetable source](../map.md)

## Question

What Euskotren feeds are published in the Moveuskadi index, how fresh are they, what validity window do they cover, and are the static and real-time endpoints actually usable?

## Answer

Resolved 2026-11-25.

- The index `last-update` is 2026-11-25 19:08:29; `data.Euskotren` lists eight feeds.
- Static GTFS: `gtfs_euskotren.zip`, 1.4 MB zipped, Last-Modified 2026-11-25 06:01 UTC, index last-update 07:01:19 local. `feed_info` says publisher Eusko Trenbideak, feed window **2026-11-25 → 2026-12-30**, version `20261125043408`. It is refreshed daily.
- The GTFS already contains the reported service: `ES:Euskotren:Journey:15521810` (and `15528810`), Durango 05:39 → Pasaia 07:55, Arroa-Zestoa 06:53, active on 2026-11-25.
- GTFS-RT: trip updates are live (268 KB, Last-Modified 18:10 UTC); vehicle positions and alerts are empty 15-byte FeedMessages at the sample time.
- NeTEx and all three SIRI XML URLs return a 5,391-byte BIG-IP logout HTML page, via both the opendata URL and the direct S3 path, even with a browser User-Agent and referer.
- The PDFs were fetched 2026-11-21; the GTFS is four days fresher and is refreshed daily with date-specific exceptions.

See [research/01-feed-freshness.md](../research/01-feed-freshness.md).

## Comments

- Charted 2026-11-25 from the live index and downloaded feeds.
