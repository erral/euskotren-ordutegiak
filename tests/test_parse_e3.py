import unittest
from pathlib import Path

from euskotren_timetable.parse_e3 import parse_e3_reverse, parse_e3_weekday

PDF = Path("data/pdfs/e3_l3.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_e3_weekday(PDF, "test")
        cls.reverse, cls.reverse_rule = parse_e3_reverse(PDF, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 62)
        self.assertEqual(len(self.reverse), 64)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "6:07")
        self.assertEqual(self.forward[-1].departure, "22:52")
        self.assertEqual(self.reverse[0].departure, "5:36")
        self.assertEqual(self.reverse[-1].departure, "22:59")

    def test_templates(self):
        self.assertEqual(len(self.forward_by["6:37"].stop_times), 16)
        self.assertEqual(len(self.reverse_by["6:06"].stop_times), 16)

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E3-L3-WD-0637-2022-15")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 56)
        self.assertEqual(self.reverse_rule.rule_id, "E3-L3-WD-0606-2021-15")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 58)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
