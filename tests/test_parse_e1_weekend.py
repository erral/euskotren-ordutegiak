import unittest
from pathlib import Path

from euskotren_timetable.parse_e1_weekend import parse_e1_weekend, parse_e1_weekend_reverse

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1WeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward, cls.forward_rule = parse_e1_weekend(FORWARD, "test")
        cls.reverse, cls.reverse_rule = parse_e1_weekend_reverse(REVERSE, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 15)
        self.assertEqual(len(self.reverse), 15)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "6:35")
        self.assertEqual(self.forward[-1].departure, "20:35")
        self.assertEqual(self.reverse[0].departure, "6:52")
        self.assertEqual(self.reverse[-1].departure, "19:52")

    def test_partial_services(self):
        forward = self.forward_by["6:35"]
        self.assertEqual(forward.origin, "Pasaia")
        self.assertEqual(forward.destination, "Deba")
        self.assertEqual(forward.pattern, ["short-turn"])
        forward_times = {st.stop_name: st.time for st in forward.stop_times}
        self.assertEqual(forward_times["Arroa (Zestoa)"], "7:33")
        self.assertEqual(forward_times["Altza (Donostia)"], "6:37")
        self.assertFalse([st for st in forward.stop_times if st.disposition == "unpublished"])

        reverse = self.reverse_by["7:44"]
        self.assertEqual(reverse.origin, "Deba")
        self.assertEqual(reverse.destination, "Pasaia")
        self.assertEqual(reverse.pattern, ["short-turn"])
        reverse_times = {st.stop_name: st.time for st in reverse.stop_times}
        self.assertEqual(reverse_times["Arroa (Zestoa)"], "7:53")
        self.assertEqual(reverse_times["Altza (Donostia)"], "8:53")
        self.assertFalse([st for st in reverse.stop_times if st.disposition == "unpublished"])

    def test_templates(self):
        for service in (self.forward_by["7:35"], self.reverse_by["6:52"]):
            self.assertEqual(len(service.stop_times), 50)
            unpublished = [st for st in service.stop_times if st.disposition == "unpublished"]
            self.assertEqual(len(unpublished), 0)

    def test_topo_merge(self):
        forward = {st.stop_name: st.time for st in self.forward_by["7:35"].stop_times}
        reverse = {st.stop_name: st.time for st in self.reverse_by["6:52"].stop_times}
        self.assertEqual(forward["Altza (Donostia)"], "7:37")
        self.assertEqual(forward["Usurbil"], "8:04")
        self.assertEqual(forward["Añorga (Donostia)"], "7:56")
        self.assertEqual(reverse["Usurbil"], "9:26")
        self.assertEqual(reverse["Añorga (Donostia)"], "9:34")
        self.assertEqual(reverse["Altza (Donostia)"], "9:53")
        self.assertIn("source side note", self.forward_by["7:35"].notes[-1])
        self.assertIn("source side note", self.reverse_by["6:52"].notes[-1])

    def test_rules(self):
        self.assertEqual(self.forward_rule.rule_id, "E1-WE-0735-2035-60")
        self.assertEqual(len(self.forward_rule.expanded_service_ids), 14)
        self.assertEqual(self.reverse_rule.rule_id, "E1-WE-0652-1952-60")
        self.assertEqual(len(self.reverse_rule.expanded_service_ids), 14)

    def test_monotonic(self):
        for service in self.forward + self.reverse:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
