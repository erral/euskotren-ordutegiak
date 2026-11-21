import unittest
from pathlib import Path

from euskotren_timetable.parse_e4 import (
    GERNIKA_WD_FORWARD,
    GERNIKA_WD_REVERSE,
    GERNIKA_WE_FORWARD,
    GERNIKA_WE_REVERSE,
    parse_e4_gernika_turns,
)

PDF = Path("data/pdfs/e4_bilbao_bermeo.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseE4GernikaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward_wd = parse_e4_gernika_turns(PDF, "test", GERNIKA_WD_FORWARD)
        cls.forward_we = parse_e4_gernika_turns(PDF, "test", GERNIKA_WE_FORWARD)
        cls.reverse_wd = parse_e4_gernika_turns(PDF, "test", GERNIKA_WD_REVERSE)
        cls.reverse_we = parse_e4_gernika_turns(PDF, "test", GERNIKA_WE_REVERSE)

    def test_counts(self):
        self.assertEqual(len(self.forward_wd), 3)
        self.assertEqual(len(self.forward_we), 2)
        self.assertEqual(len(self.reverse_wd), 1)
        self.assertEqual(len(self.reverse_we), 1)

    def test_destinations(self):
        self.assertTrue(all(s.destination == "Bermeo" for s in self.forward_wd))
        self.assertTrue(all(s.destination == "Bermeo" for s in self.forward_we))
        self.assertTrue(all(s.destination == "Matiko-Bilbao" for s in self.reverse_wd))
        self.assertTrue(all(s.destination == "Matiko-Bilbao" for s in self.reverse_we))

    def test_origins_and_pattern(self):
        for service in self.forward_wd + self.forward_we + self.reverse_wd + self.reverse_we:
            self.assertEqual(service.origin, "Gernika")
            self.assertEqual(service.pattern, ["short-turn"])
            self.assertIn("Gernika short-turn", service.notes)


if __name__ == "__main__":
    unittest.main()
