# Feed inventory and freshness

Evidence collected 2026-11-25.

## Source

The Moveuskadi index is `data-index.json` at:

`https://s3.itbatera.euskadi.eus/02-pro-e3525cfb1b3d99109c5220a2b24bcb30-inet/transport/moveuskadi/data-index.json`

- `last-update`: **2026-11-25 19:08:29**
- The index is 47 KB and has 35 operator keys under `data`.
- The `data.Euskotren` entry has eight feeds.

## Euskotren feeds

| Format | File | Index last-update |
|---|---|---|
| GTFS | `gtfs_euskotren.zip` | 2026-11-25 07:01:19 |
| NETEX | `netex_euskotren.zip` | 2026-11-25 07:01:18 |
| GTFS-RT | `gtfsrt_euskotren_trip_updates.pb` | 2026-11-25 19:08:27 |
| GTFS-RT | `gtfsrt_euskotren_vehicle_positions.pb` | 2026-11-25 04:32:28 |
| GTFS-RT | `gtfsrt_euskotren_alerts.pb` | 2026-11-25 18:54:31 |
| SIRI | `siri_euskotren_situation_exchange.xml` | 2026-11-25 19:08:27 |
| SIRI | `siri_euskotren_vehicle_monitoring.xml` | 2026-11-25 19:08:27 |
| SIRI | `siri_euskotren_estimated_timetable.xml` | 2026-11-25 19:08:27 |

## Static GTFS

- URL: `https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip`
- 1.4 MB zipped, 13.7 MB expanded.
- `Last-Modified`: **2026-11-25 06:01:19 UTC** (07:01:19 Europe/Madrid).
- `feed_info.txt`:
  - publisher: Eusko Trenbideak
  - `feed_start_date`: **20261125**
  - `feed_end_date`: **20261230**
  - `feed_version`: **20261125043408**
  - language: `eu`
- Contents: `agency`, `attributions`, `calendar`, `calendar_dates`, `fare_attributes`, `fare_rules`, `levels`, `pathways`, `routes`, `shapes`, `transfers`, `translations`, `trips`, `stops`, `stop_times`, `feed_info`.
- It is a rolling feed: it starts today and ends 2026-12-30. It must be refreshed to keep a static build current.

## The reported Arroa service is in GTFS

A stop-time search for `Arroa-Zestoa` at 06:53 returns two trips on the same pattern:

- `ES:Euskotren:Journey:15521810` — route E1, service `ES:Euskotren:Service:3107:`
- `ES:Euskotren:Journey:15528810` — route E1, service `ES:Euskotren:Service:3108:`

Both run:

`Durango 05:39 → ... → Arroa-Zestoa 06:53 → Zumaia 06:57/07:00 → ... → Pasaia 07:55`

The service_id split is calendar-driven (3107 is Mon–Thu, 3108 is Friday); the times are identical. The service is active on 2026-11-25.

This is the service our PDF parser had missed and that we restored in commit `bc95083`. GTFS contained it already.

## Real-time and XML feeds

- **GTFS-RT trip updates**: 268 KB protobuf, `Last-Modified` 2026-11-25 18:10:33 UTC. Contains live `TripUpdate` entries; sampled bytes show GTFS-RT 2.0.
- **GTFS-RT vehicle positions**: 15-byte protobuf (an empty `FeedMessage` with only a header) at the sample time; `Last-Modified` 2026-11-25 03:32:28 UTC.
- **GTFS-RT alerts**: 15-byte empty `FeedMessage`; `Last-Modified` 2026-11-25 17:54:31 UTC.
- **NeTEx zip and all three SIRI XML files**: the listed URL, and the direct S3 path, return a 5,391-byte **BIG-IP logout HTML page** with `Content-Type: application/zip` / `application/xml`. A browser User-Agent and referer do not change the result. They are not usable as published.

## PDF freshness comparison

- The six PDFs were fetched **2026-11-21** and are valid from 2026-11-21 with an open end.
- The GTFS was built on **2026-11-25** and is refreshed daily around 07:00 local.
- The GTFS also carries date-specific `calendar_dates` exceptions for the Christmas period; the PDFs only carry generic day-type blocks.
- The PDFs remain the visual/provenance source and cover the season from 2026-11-21, four days before the GTFS window starts.

## Conclusion

The static GTFS is fresh, complete enough to contain the service the PDF pipeline missed, and far easier to consume than coordinate-based PDF parsing. The real-time feeds are not a substitute for the static timetable: only trip updates are currently populated, and the SIRI/NeTEx endpoints are blocked.
