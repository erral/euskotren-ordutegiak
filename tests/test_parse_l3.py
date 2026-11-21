import unittest
from pathlib import Path

from euskotren_timetable.parse_l3 import parse_l3_reverse, parse_l3_weekday

PDF = Path("data/pdfs/e3_l3.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseL3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_l3_weekday(PDF, "test")
        cls.reverse, cls.reverse_rule = parse_l3_reverse(PDF, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 138)
        self.assertEqual(len(self.reverse), 140)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "5:55")
        self.assertEqual(self.forward[-1].departure, "23:02")
        self.assertEqual(self.reverse[0].departure, "5:36")
        self.assertEqual(self.reverse[-1].departure, "23:14")

    def test_templates(self):
        self.assertEqual(len(self.forward_by["5:55"].stop_times), 7)
        self.assertEqual(len(self.reverse_by["5:51"].stop_times), 7)

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E3-L3-WD-0555-2302-7.5")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 138)
        self.assertEqual(self.reverse_rule.rule_id, "E3-L3-WD-0551-2259-7.5")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 138)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
