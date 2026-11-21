import unittest
from pathlib import Path

from euskotren_timetable.parse_e4 import parse_e4_reverse, parse_e4_weekday

PDF = Path("data/pdfs/e4_bilbao_bermeo.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_e4_weekday(PDF, "test")
        cls.reverse, cls.reverse_rule = parse_e4_reverse(PDF, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 33)
        self.assertEqual(len(self.reverse), 32)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "6:10")
        self.assertEqual(self.forward[-1].departure, "22:10")
        self.assertEqual(self.reverse[0].departure, "6:18")
        self.assertEqual(self.reverse[-1].departure, "22:35")

    def test_templates(self):
        self.assertEqual(len(self.forward_by["6:10"].stop_times), 25)
        self.assertEqual(len(self.reverse_by["6:18"].stop_times), 25)

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E4-WD-0710-1910-30")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 25)
        self.assertEqual(self.reverse_rule.rule_id, "E4-WD-0618-2048-30")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 30)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
