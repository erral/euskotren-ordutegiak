import unittest
from pathlib import Path

from euskotren_timetable.parse_e1_eibar import parse_e1_eibar

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1EibarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services, cls.rules = parse_e1_eibar(FORWARD, REVERSE, "test", "test")
        cls.by_id = {service.service_id: service for service in cls.services}

    def test_counts(self):
        self.assertEqual(len(self.services), 214)

    def test_first_last(self):
        wd = [s for s in self.services if s.service_id.startswith("E1-EIBAR-ERMUA") and s.calendar == "WD"]
        we = [s for s in self.services if s.service_id.startswith("E1-EIBAR-ERMUA") and s.calendar == "WE"]
        rwd = [s for s in self.services if s.service_id.startswith("E1-ERMUA-EIBAR") and s.calendar == "WD"]
        rwe = [s for s in self.services if s.service_id.startswith("E1-ERMUA-EIBAR") and s.calendar == "WE"]
        self.assertEqual((wd[0].departure, wd[-1].departure), ("6:11", "22:11"))
        self.assertEqual((we[0].departure, we[-1].departure), ("8:00", "22:11"))
        self.assertEqual((rwd[0].departure, rwd[-1].departure), ("6:01", "22:01"))
        self.assertEqual((rwe[0].departure, rwe[-1].departure), ("8:01", "22:02"))

    def test_rules(self):
        rules = {rule.rule_id: rule for rule in self.rules}
        self.assertEqual(len(rules["E1-EIBAR-ERMUA-WD-0641-2211-60"].expanded_service_ids), 63)
        self.assertEqual(len(rules["E1-EIBAR-ERMUA-WE-0800-2211-60"].expanded_service_ids), 44)
        self.assertEqual(len(rules["E1-ERMUA-EIBAR-WD-0631-2131-60"].expanded_service_ids), 61)
        self.assertEqual(len(rules["E1-ERMUA-EIBAR-WE-0801-2142-60"].expanded_service_ids), 42)

    def test_hourly_repeat(self):
        service = self.by_id["E1-EIBAR-ERMUA-WD-0800"]
        self.assertEqual(service.departure, "8:00")
        self.assertEqual(service.destination, "Ermua")
        self.assertEqual(len(service.stop_times), 7)


if __name__ == "__main__":
    unittest.main()
