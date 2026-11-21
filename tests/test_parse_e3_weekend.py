import unittest
from pathlib import Path

from euskotren_timetable.parse_e3 import parse_e3_weekend, parse_e3_weekend_reverse

PDF = Path("data/pdfs/e3_l3.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE3WeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_e3_weekend(PDF, "test")
        cls.reverse, cls.reverse_rule = parse_e3_weekend_reverse(PDF, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 32)
        self.assertEqual(len(self.reverse), 31)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "7:37")
        self.assertEqual(self.forward[-1].departure, "23:07")
        self.assertEqual(self.reverse[0].departure, "7:24")
        self.assertEqual(self.reverse[-1].departure, "22:24")

    def test_templates(self):
        self.assertEqual(len(self.forward_by["7:37"].stop_times), 16)
        self.assertEqual(len(self.reverse_by["7:24"].stop_times), 16)

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E3-L3-WE-0737-2237-30")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 31)
        self.assertEqual(self.reverse_rule.rule_id, "E3-L3-WE-0724-2224-30")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 31)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
