import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from euskotren_timetable.gtfs import LINE_CALENDARS, load_gtfs_services
from euskotren_timetable.gtfs_stops import GTFS_STOP_ALIASES, canonical_stop

FULL_FEED = Path("data/gtfs/gtfs_euskotren.zip")


def _write_feed(directory: Path) -> Path:
    path = directory / "feed.zip"
    files = {
        "routes.txt": ("route_id,route_short_name\nR_E1,E1\n"),
        "trips.txt": ("route_id,service_id,trip_id\nR_E1,SVC,T1\n"),
        "stops.txt": (
            "stop_id,stop_name,parent_station,location_type\n"
            "ES:Euskotren:StopPlace:2667:,Pasaia,,1\n"
            "ES:Euskotren:Quay:2667_Q1:,Pasaia,ES:Euskotren:StopPlace:2667:,0\n"
            "ES:Euskotren:StopPlace:2631:,Altza-Donostia,,1\n"
            "ES:Euskotren:Quay:2631_Q1:,Altza-Donostia,ES:Euskotren:StopPlace:2631:,0\n"
            "ES:Euskotren:StopPlace:2597:,Matiko-Bilbao,,1\n"
            "ES:Euskotren:Quay:2597_Q1:,Matiko-Bilbao,ES:Euskotren:StopPlace:2597:,0\n"
        ),
        "stop_times.txt": (
            "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
            "T1,05:35:00,05:35:00,ES:Euskotren:Quay:2667_Q1:,1\n"
            "T1,05:37:00,05:37:00,ES:Euskotren:Quay:2631_Q1:,2\n"
            "T1,06:00:00,06:00:00,ES:Euskotren:Quay:2597_Q1:,3\n"
        ),
        "calendar.txt": (
            "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
            "SVC,1,1,1,1,1,1,1,20261125,20261230\n"
        ),
        "calendar_dates.txt": "service_id,date,exception_type\n",
        "feed_info.txt": (
            "feed_publisher_name,feed_version,feed_start_date,feed_end_date\n"
            "Eusko Trenbideak,20261125000000,20261125,20261230\n"
        ),
    }
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return path


class GtfsAdapterTests(unittest.TestCase):
    def test_stop_alias_lookup(self):
        self.assertEqual(
            canonical_stop("ES:Euskotren:StopPlace:2613:", "Arroa-Zestoa"),
            "Arroa (Zestoa)",
        )
        with self.assertRaises(ValueError):
            canonical_stop("ES:Euskotren:StopPlace:999999:", "Missing")

    def test_alias_table_is_one_to_one(self):
        canonical = [value[1] for value in GTFS_STOP_ALIASES.values()]
        self.assertEqual(len(canonical), len(set(canonical)))

    def test_synthetic_feed(self):
        with TemporaryDirectory() as temp:
            feed = _write_feed(Path(temp))
            services, meta = load_gtfs_services(feed, source_url="test://feed")
        self.assertEqual(meta.feed_version, "20261125000000")
        self.assertEqual(meta.feed_start_date, "2026-11-25")
        self.assertEqual(meta.feed_end_date, "2026-12-30")
        self.assertEqual({service.calendar for service in services}, {"WD", "SA", "SU", "WE"})
        service = next(service for service in services if service.calendar == "WD")
        self.assertEqual(service.service_id, "E1-PASAIA-MATIKO-WD-0535")
        self.assertEqual(service.origin, "Pasaia")
        self.assertEqual(service.destination, "Matiko-Bilbao")
        self.assertEqual(service.departure, "5:35")
        self.assertEqual(service.arrival, "6:00")
        self.assertEqual(service.pattern, ["through"])
        self.assertEqual(service.gtfs_trip_id, "T1")
        self.assertEqual(service.gtfs_service_id, "SVC")
        self.assertEqual(meta.as_manifest()["source"], "gtfs")

    @unittest.skipUnless(FULL_FEED.exists(), "run the GTFS download first")
    def test_full_feed_invariants(self):
        services, meta = load_gtfs_services(FULL_FEED)
        self.assertGreater(len(services), 0)
        self.assertTrue(all(service.gtfs_trip_id for service in services))
        for service in services:
            self.assertIn(service.calendar, LINE_CALENDARS[service.primary_line])
        arroa = [
            service
            for service in services
            if service.primary_line == "E1"
            and any(
                stop.stop_name == "Arroa (Zestoa)" and stop.time == "6:53"
                for stop in service.stop_times
            )
        ]
        self.assertTrue(arroa, "the reported Arroa 06:53 service should be present")


if __name__ == "__main__":
    unittest.main()
