import unittest
from pathlib import Path

from euskotren_timetable.parse_e2 import parse_e2_reverse, parse_e2_weekday

PDF = Path("data/pdfs/e2_t1_hendaia_lasarte.pdf")
PDF_REV = Path("data/pdfs/e2_t1_lasarte_hendaia.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services, cls.rules = parse_e2_weekday(PDF, "test")
        cls.full = [service for service in cls.services if service.origin == "Hendaia"]
        cls.partial = [service for service in cls.services if service.origin == "Pasaia"]
        cls.full_by = {service.departure: service for service in cls.full}
        cls.partial_by = {service.departure: service for service in cls.partial}

    def test_counts(self):
        self.assertEqual(len(self.full), 35)
        self.assertEqual(len(self.partial), 139)

    def test_full_template(self):
        service = self.full_by["5:34"]
        self.assertEqual(len(service.stop_times), 23)
        gaintxurizketa = next(
            st.time for st in service.stop_times if st.stop_name == "Gaintxurizketa (Lezo)"
        )
        self.assertEqual(gaintxurizketa, "5:47")

    def test_partial_template(self):
        service = self.partial_by["5:28"]
        self.assertEqual(len(service.stop_times), 11)

    def test_frequencies(self):
        by_interval = {rule.interval_minutes: rule for rule in self.rules}
        self.assertEqual(len(by_interval[30].expanded_service_ids), 33)
        self.assertEqual(len(by_interval[7.5].expanded_service_ids), 137)

    def test_monotonic(self):
        for service in self.services:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


@unittest.skipUnless(PDF_REV.exists(), "run the manifest first")
class ParseE2ReverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services, cls.rules = parse_e2_reverse(PDF_REV, "test")
        cls.full = [service for service in cls.services if service.origin == "Lasarte-Oria"]
        cls.partial = [service for service in cls.services if service.origin == "Añorga (Donostia)"]
        cls.full_by = {service.departure: service for service in cls.full}
        cls.partial_by = {service.departure: service for service in cls.partial}

    def test_counts(self):
        self.assertEqual(len(self.full), 34)
        self.assertEqual(len(self.partial), 136)

    def test_full_template(self):
        self.assertEqual(len(self.full_by["6:05"].stop_times), 23)

    def test_partial_template(self):
        self.assertEqual(len(self.partial_by["6:11"].stop_times), 11)

    def test_frequencies(self):
        by_interval = {rule.interval_minutes: rule for rule in self.rules}
        self.assertEqual(len(by_interval[30].expanded_service_ids), 34)
        self.assertEqual(len(by_interval[7.5].expanded_service_ids), 133)

    def test_monotonic(self):
        for service in self.services:
            times = [st.time for st in service.stop_times if st.time and st.time != "?"]
            minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
