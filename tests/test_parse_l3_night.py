import unittest
from pathlib import Path

from euskotren_timetable.parse_e1 import to_minutes
from euskotren_timetable.parse_l3_night import parse_e3_night, parse_l3_night

PDF = Path("data/pdfs/e3_l3.pdf")


@unittest.skipUnless(PDF.exists(), "run the manifest first")
class ParseL3NightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l3, cls.rules = parse_l3_night(PDF, "test")
        cls.e3 = parse_e3_night(PDF, "test")
        cls.by_key = {(s.calendar, s.direction, s.departure): s for s in cls.l3}
        cls.e3_by = {(s.direction, s.departure): s for s in cls.e3}

    def test_counts(self):
        self.assertEqual(len(self.l3), 79)
        self.assertEqual(len(self.e3), 11)

    def test_l3_first_last(self):
        fn = [s for s in self.l3 if s.calendar == "FN" and s.direction == "Matiko-Kukullaga"]
        sn = [s for s in self.l3 if s.calendar == "SN" and s.direction == "Matiko-Kukullaga"]
        fnr = [s for s in self.l3 if s.calendar == "FN" and s.direction == "Kukullaga-Matiko"]
        snr = [s for s in self.l3 if s.calendar == "SN" and s.direction == "Kukullaga-Matiko"]
        self.assertEqual((fn[0].departure, fn[-1].departure), ("23:12", "26:15"))
        self.assertEqual((sn[0].departure, sn[-1].departure), ("23:18", "29:45"))
        self.assertEqual((fnr[0].departure, fnr[-1].departure), ("23:24", "26:08"))
        self.assertEqual((snr[0].departure, snr[-1].departure), ("23:38", "29:53"))

    def test_l3_rules(self):
        rules = {rule.rule_id: rule for rule in self.rules}
        self.assertEqual(
            len(rules["E3-L3-MATIKO-KUKULLAGA-FN-2330-0215-15"].expanded_service_ids), 12
        )
        self.assertEqual(
            len(rules["E3-L3-MATIKO-KUKULLAGA-SN-2345-0545-15"].expanded_service_ids), 25
        )
        self.assertEqual(
            len(rules["E3-L3-KUKULLAGA-MATIKO-FN-2338-0208-15"].expanded_service_ids), 11
        )
        self.assertEqual(
            len(rules["E3-L3-KUKULLAGA-MATIKO-SN-2338-0553-15"].expanded_service_ids), 26
        )

    def test_e3_explicit(self):
        forward = [s for s in self.e3 if s.direction == "Lezama-Kukullaga"]
        reverse = [s for s in self.e3 if s.direction == "Kukullaga-Lezama"]
        self.assertEqual(
            [s.departure for s in forward], ["23:07", "23:50", "24:51", "26:51", "28:51", "30:57"]
        )
        self.assertEqual(
            [s.departure for s in reverse], ["22:54", "24:08", "26:08", "28:08", "30:08"]
        )

    def test_day_offsets(self):
        service = self.by_key[("FN", "Matiko-Kukullaga", "24:00")]
        matiko = next(st for st in service.stop_times if st.stop_name == "Matiko-Bilbao")
        kukullaga = next(st for st in service.stop_times if st.stop_name == "Kukullaga-Etxebarri")
        self.assertEqual((matiko.time, matiko.day_offset), ("24:00", 1))
        self.assertEqual((kukullaga.time, kukullaga.day_offset), ("24:11", 1))
        e3 = self.e3_by[("Lezama-Kukullaga", "23:50")]
        lezama = next(st for st in e3.stop_times if st.stop_name == "Lezama")
        kukullaga = next(st for st in e3.stop_times if st.stop_name == "Kukullaga-Etxebarri")
        self.assertEqual(lezama.day_offset, 0)
        self.assertEqual((kukullaga.time, kukullaga.day_offset), ("24:26", 1))

    def test_monotonic(self):
        for services in (self.l3, self.e3):
            for service in services:
                minutes = [
                    to_minutes(st.time) for st in service.stop_times if st.time and st.time != "?"
                ]
                self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
