import unittest
from pathlib import Path

from euskotren_timetable.parse_e1 import ALTZOLA, parse_e1_weekday

PDF = Path("data/pdfs/e1_pasaia_matiko.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services, cls.rule = parse_e1_weekday(PDF, "test")
        cls.by_departure = {service.departure: service for service in cls.services}

    def test_service_count(self):
        self.assertEqual(len(self.services), 16)

    def test_template_complete(self):
        service = self.by_departure["5:35"]
        self.assertEqual(len(service.stop_times), 50)
        self.assertFalse([st for st in service.stop_times if st.disposition == "unpublished"])

    def test_frequency_rule(self):
        self.assertEqual(self.rule.interval_minutes, 60)
        self.assertEqual(self.rule.start, "5:35")
        self.assertEqual(self.rule.end, "19:35")
        self.assertEqual(len(self.rule.expanded_service_ids), 15)

    def test_altzola_footnote(self):
        expected = {"7:35": "8:56", "11:35": "12:56", "18:35": "19:56", "20:35": "21:56"}
        for departure, value in expected.items():
            service = self.by_departure[departure]
            actual = next(st.time for st in service.stop_times if st.stop_name == ALTZOLA)
            self.assertEqual(actual, value, departure)

    def test_altzola_pass(self):
        service = self.by_departure["6:35"]
        stop = next(st for st in service.stop_times if st.stop_name == ALTZOLA)
        self.assertEqual(stop.disposition, "pass")

    def test_monotonic(self):
        for service in self.services:
            times = [
                st.time
                for st in service.stop_times
                if st.time and st.time != "?"
            ]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
