import unittest
from pathlib import Path

from euskotren_timetable.parse_e1_refuerzo import parse_e1_refuerzos

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1RefuerzoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services = parse_e1_refuerzos(FORWARD, REVERSE, "test", "test")
        cls.by_id = {service.service_id: service for service in cls.services}

    def test_count(self):
        self.assertEqual(len(self.services), 5)

    def test_zaldibar(self):
        service = self.by_id["E1-ZALDIBAR-MATIKO-WD-0642"]
        self.assertEqual(service.origin, "Zaldibar")
        self.assertEqual(service.destination, "Matiko-Bilbao")
        self.assertEqual(service.departure, "6:42")
        self.assertEqual(service.pattern, ["refuerzo"])

    def test_trana_rows(self):
        durango = self.by_id["E1-MATIKO-TRANA-WD-0732"]
        trana = self.by_id["E1-MATIKO-TRANA-WD-0832"]
        self.assertEqual(durango.destination, "Durango")
        self.assertEqual(trana.destination, "Traña Abadiño")
        self.assertEqual(len(trana.stop_times), 17)

    def test_passes(self):
        service = self.by_id["E1-ZALDIBAR-MATIKO-WD-0642"]
        passes = [st.stop_name for st in service.stop_times if st.disposition == "pass"]
        self.assertIn("Amorebieta Geltokia", passes)
        self.assertIn("Etxebarri", passes)


if __name__ == "__main__":
    unittest.main()
