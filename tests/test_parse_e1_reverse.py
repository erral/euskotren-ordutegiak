import unittest
from pathlib import Path

from euskotren_timetable.parse_e1_reverse import parse_e1_reverse

PDF = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE1ReverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services, cls.rule = parse_e1_reverse(PDF, "test")
        cls.by_departure = {service.departure: service for service in cls.services}

    def test_count(self):
        self.assertEqual(len(self.services), 15)

    def test_first_last(self):
        self.assertEqual(self.services[0].departure, "5:55")
        self.assertEqual(self.services[-1].departure, "19:55")

    def test_template(self):
        service = self.by_departure["5:55"]
        self.assertEqual(len(service.stop_times), 50)
        unpublished = [st for st in service.stop_times if st.disposition == "unpublished"]
        self.assertEqual(len(unpublished), 0)

    def test_topo_merge(self):
        service = self.by_departure["5:55"]
        times = {st.stop_name: st.time for st in service.stop_times}
        self.assertEqual(times["Usurbil"], "8:26")
        self.assertEqual(times["Añorga (Donostia)"], "8:34")
        self.assertEqual(times["Altza (Donostia)"], "8:53")
        self.assertIn("Topo times from Zumaia-Pasaia partial table", service.notes)

    def test_altzola(self):
        # Only the 19:55 full-line service brackets its footnote time.
        # The 6:26/10:26/13:26 times belong to deferred partial services.
        expected = {"5:55": None, "9:55": None, "12:55": None, "19:55": "21:26"}
        for departure, value in expected.items():
            service = self.by_departure[departure]
            actual = next(
                st.time for st in service.stop_times if st.stop_name == "Altzola (Elgoibar)"
            )
            self.assertEqual(actual, value, departure)

    def test_rule(self):
        self.assertEqual(self.rule.rule_id, "E1-WD-0555-1955-60")
        self.assertEqual(self.rule.interval_minutes, 60)
        self.assertEqual(len(self.rule.expanded_service_ids), 15)

    def test_monotonic(self):
        for service in self.services:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
