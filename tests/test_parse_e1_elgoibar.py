import unittest
from pathlib import Path

from euskotren_timetable.parse_e1_elgoibar import parse_e1_elgoibar

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1ElgoibarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = parse_e1_elgoibar(FORWARD, REVERSE, "test", "test")
        cls.by_id = {service.service_id: service for service in cls.services}

    def test_counts(self):
        self.assertEqual(len(self.services), 79)

    def test_first_last(self):
        wd = [
            s
            for s in self.services
            if s.service_id.startswith("E1-ELGOIBAR-MATIKO") and s.calendar == "WD"
        ]
        we = [
            s
            for s in self.services
            if s.service_id.startswith("E1-ELGOIBAR-MATIKO") and s.calendar == "WE"
        ]
        rwd = [
            s
            for s in self.services
            if s.service_id.startswith("E1-MATIKO-ELGOIBAR") and s.calendar == "WD"
        ]
        rwe = [
            s
            for s in self.services
            if s.service_id.startswith("E1-MATIKO-ELGOIBAR") and s.calendar == "WE"
        ]
        self.assertEqual((wd[0].departure, wd[-1].departure), ("7:01", "22:01"))
        self.assertEqual((we[0].departure, we[-1].departure), ("9:01", "22:01"))
        self.assertEqual((rwd[0].departure, rwd[-1].departure), ("5:55", "19:55"))
        self.assertEqual((rwe[0].departure, rwe[-1].departure), ("6:52", "19:52"))

    def test_sample(self):
        service = self.by_id["E1-ELGOIBAR-MATIKO-WD-1801"]
        self.assertEqual(service.origin, "Elgoibar")
        self.assertEqual(service.destination, "Matiko-Bilbao")
        self.assertEqual(service.departure, "18:01")
        self.assertEqual(service.arrival, "19:25")

    def test_durango_short_turn(self):
        service = self.by_id["E1-ELGOIBAR-MATIKO-WD-2201"]
        self.assertEqual(service.destination, "Durango")


if __name__ == "__main__":
    unittest.main()
