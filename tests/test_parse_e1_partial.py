import unittest
from pathlib import Path

from euskotren_timetable.parse_e1 import parse_e1_weekday
from euskotren_timetable.parse_e1_partial import (
    FORWARD_SATURDAY,
    FORWARD_SUNDAY,
    FORWARD_WEEKDAY,
    REVERSE_SATURDAY,
    REVERSE_SUNDAY,
    REVERSE_WEEKDAY,
    build_partial_services,
)
from euskotren_timetable.parse_e1_reverse import parse_e1_reverse
from euskotren_timetable.parse_e1_weekend import parse_e1_weekend, parse_e1_weekend_reverse

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1PartialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e1w, _ = parse_e1_weekday(FORWARD, "test")
        e1e, _ = parse_e1_reverse(REVERSE, "test")
        e1we, _ = parse_e1_weekend(FORWARD, "test")
        e1ww, _ = parse_e1_weekend_reverse(REVERSE, "test")
        cls.e1w_times = {service.departure for service in e1w}
        cls.e1we_times = {service.departure for service in e1we}
        cls.e1e_zumaia = {
            next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
            for service in e1e
        }
        cls.e1ww_zumaia = {
            next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
            for service in e1ww
        }
        cls.wd = build_partial_services(
            FORWARD, "test", FORWARD_WEEKDAY, cls.e1w_times, "Pasaia-Matiko", "PASAIA-ZUMAIA"
        )
        cls.sa = build_partial_services(
            FORWARD, "test", FORWARD_SATURDAY, cls.e1we_times, "Pasaia-Matiko", "PASAIA-ZUMAIA"
        )
        cls.su = build_partial_services(
            FORWARD, "test", FORWARD_SUNDAY, cls.e1we_times, "Pasaia-Matiko", "PASAIA-ZUMAIA"
        )
        cls.rwd = build_partial_services(
            REVERSE, "test", REVERSE_WEEKDAY, cls.e1e_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA"
        )
        cls.rsa = build_partial_services(
            REVERSE, "test", REVERSE_SATURDAY, cls.e1ww_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA"
        )
        cls.rsu = build_partial_services(
            REVERSE, "test", REVERSE_SUNDAY, cls.e1ww_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA"
        )

    def test_counts(self):
        self.assertEqual(len(self.wd), 17)
        self.assertEqual(len(self.sa), 16)
        self.assertEqual(len(self.su), 10)
        self.assertEqual(len(self.rwd), 18)
        self.assertEqual(len(self.rsa), 17)
        self.assertEqual(len(self.rsu), 9)

    def test_first_last(self):
        self.assertEqual((self.wd[0].departure, self.wd[-1].departure), ("6:05", "21:35"))
        self.assertEqual((self.sa[0].departure, self.sa[-1].departure), ("7:05", "21:35"))
        self.assertEqual((self.su[0].departure, self.su[-1].departure), ("13:05", "21:35"))
        self.assertEqual((self.rwd[0].departure, self.rwd[-1].departure), ("6:00", "22:31"))
        self.assertEqual((self.rsa[0].departure, self.rsa[-1].departure), ("7:00", "22:31"))
        self.assertEqual((self.rsu[0].departure, self.rsu[-1].departure), ("14:30", "22:31"))

    def test_sample(self):
        service = {s.departure: s for s in self.wd}["6:05"]
        self.assertEqual(service.origin, "Pasaia")
        self.assertEqual(service.destination, "Zumaia")
        self.assertEqual(service.pattern, ["short-turn"])
        self.assertEqual(len(service.stop_times), 17)
        self.assertNotIn("6:05", self.e1w_times)

    def test_no_full_line_duplicates(self):
        for service in self.wd:
            self.assertNotIn(service.departure, self.e1w_times)
        for service in self.sa + self.su:
            self.assertNotIn(service.departure, self.e1we_times)
        for service in self.rwd:
            self.assertNotIn(service.departure, self.e1e_zumaia)
        for service in self.rsa + self.rsu:
            self.assertNotIn(service.departure, self.e1ww_zumaia)


if __name__ == "__main__":
    unittest.main()
