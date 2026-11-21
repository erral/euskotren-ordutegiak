import unittest
from pathlib import Path

from euskotren_timetable.parse_e1 import to_minutes
from euskotren_timetable.parse_night import (
    parse_e2_night,
    parse_e2_night_reverse,
    parse_e4_night,
    parse_e4_night_reverse,
)

E2_FORWARD = Path("data/pdfs/e2_t1_hendaia_lasarte.pdf")
E2_REVERSE = Path("data/pdfs/e2_t1_lasarte_hendaia.pdf")
E4 = Path("data/pdfs/e4_bilbao_bermeo.pdf")


@unittest.skipUnless(
    E2_FORWARD.exists() and E2_REVERSE.exists() and E4.exists(),
    "run the manifest first",
)
class ParseNightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e2_forward = parse_e2_night(E2_FORWARD, "test")
        cls.e2_reverse = parse_e2_night_reverse(E2_REVERSE, "test")
        cls.e4_forward = parse_e4_night(E4, "test")
        cls.e4_reverse = parse_e4_night_reverse(E4, "test")
        cls.e2_forward_by = {s.departure: s for s in cls.e2_forward}
        cls.e2_reverse_by = {s.departure: s for s in cls.e2_reverse}
        cls.e4_forward_by = {s.departure: s for s in cls.e4_forward}
        cls.e4_reverse_by = {s.departure: s for s in cls.e4_reverse}

    def test_counts(self):
        self.assertEqual(len(self.e2_forward), 8)
        self.assertEqual(len(self.e2_reverse), 8)
        self.assertEqual(len(self.e4_forward), 5)
        self.assertEqual(len(self.e4_reverse), 5)

    def test_first_last(self):
        self.assertEqual(self.e2_forward[0].departure, "23:04")
        self.assertEqual(self.e2_forward[-1].departure, "26:34")
        self.assertEqual(self.e2_reverse[0].departure, "23:05")
        self.assertEqual(self.e2_reverse[-1].departure, "26:35")
        self.assertEqual(self.e4_forward[0].departure, "22:12")
        self.assertEqual(self.e4_forward[-1].departure, "29:45")
        self.assertEqual(self.e4_reverse[0].departure, "23:34")
        self.assertEqual(self.e4_reverse[-1].departure, "31:25")

    def test_e2_full_line(self):
        service = self.e2_forward_by["23:34"]
        stops = [st for st in service.stop_times if st.disposition == "stop"]
        self.assertEqual(len(stops), 23)
        self.assertEqual(service.arrival, "24:25")

    def test_e4_specials(self):
        bermeo = self.e4_forward_by["22:12"]
        self.assertEqual(bermeo.destination, "Bermeo")
        self.assertEqual(len([st for st in bermeo.stop_times if st.disposition == "stop"]), 25)
        amorebieta = self.e4_reverse_by["23:34"]
        self.assertEqual(amorebieta.destination, "Amorebieta Geltokia")
        geltokia = next(st for st in bermeo.stop_times if st.stop_name == "Amorebieta Geltokia")
        self.assertEqual(geltokia.disposition, "pass")
        gernika = self.e4_reverse_by["31:25"]
        self.assertEqual(gernika.destination, "Gernika")

    def test_day_offsets(self):
        e2 = self.e2_forward_by["23:34"]
        hendaya = next(st for st in e2.stop_times if st.stop_name == "Hendaia")
        lasarte = next(st for st in e2.stop_times if st.stop_name == "Lasarte-Oria")
        self.assertEqual((hendaya.time, hendaya.day_offset), ("23:34", 0))
        self.assertEqual((lasarte.time, lasarte.day_offset), ("24:25", 1))
        special = self.e4_forward_by["22:12"]
        bermeo = next(st for st in special.stop_times if st.stop_name == "Bermeo")
        self.assertEqual((bermeo.time, bermeo.day_offset), ("23:32", 0))

    def test_monotonic(self):
        for services in (
            self.e2_forward,
            self.e2_reverse,
            self.e4_forward,
            self.e4_reverse,
        ):
            for service in services:
                minutes = [
                    to_minutes(st.time) for st in service.stop_times if st.time and st.time != "?"
                ]
                self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
