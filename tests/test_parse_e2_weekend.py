import unittest
from pathlib import Path

from euskotren_timetable.parse_e2_weekend import parse_e2_weekend, parse_e2_weekend_reverse

FORWARD = Path("data/pdfs/e2_t1_hendaia_lasarte.pdf")
REVERSE = Path("data/pdfs/e2_t1_lasarte_hendaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE2WeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_e2_weekend(FORWARD, "test")
        cls.reverse, cls.reverse_rule = parse_e2_weekend_reverse(REVERSE, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 33)
        self.assertEqual(len(self.reverse), 33)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "6:34")
        self.assertEqual(self.forward[-1].departure, "22:34")
        self.assertEqual(self.reverse[0].departure, "6:35")
        self.assertEqual(self.reverse[-1].departure, "22:35")

    def test_templates(self):
        self.assertEqual(len(self.forward_by["6:34"].stop_times), 23)
        self.assertEqual(len(self.reverse_by["6:35"].stop_times), 23)

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E2-T1-WE-0634-2234-30")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 33)
        self.assertEqual(self.reverse_rule.rule_id, "E2-T1-WE-0635-2235-30")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 33)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
