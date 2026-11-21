import unittest
from pathlib import Path

from euskotren_timetable.parse_e1 import to_minutes
from euskotren_timetable.parse_e1_night import parse_e1_night, parse_e1_night_reverse

FORWARD = Path("data/pdfs/e1_pasaia_matiko.pdf")
REVERSE = Path("data/pdfs/e1_matiko_pasaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE1NightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward = parse_e1_night(FORWARD, "test")
        cls.reverse = parse_e1_night_reverse(REVERSE, "test")
        cls.forward_by = {service.departure: service for service in cls.forward}
        cls.reverse_by = {service.departure: service for service in cls.reverse}

    def test_counts(self):
        self.assertEqual(len(self.forward), 4)
        self.assertEqual(len(self.reverse), 4)

    def test_first_last(self):
        self.assertEqual(self.forward[0].departure, "25:37")
        self.assertEqual(self.forward[-1].departure, "31:19")
        self.assertEqual(self.reverse[0].departure, "23:45")
        self.assertEqual(self.reverse[-1].departure, "29:45")

    def test_destinations(self):
        self.assertEqual(self.forward[0].destination, "Matiko-Bilbao")
        self.assertEqual(self.forward[-1].destination, "Durango")
        self.assertEqual(self.reverse[0].destination, "Deba")
        self.assertEqual(self.reverse[-1].destination, "Elgoibar")

    def test_day_offsets(self):
        forward = self.forward_by["25:37"]
        self.assertTrue(
            all(st.day_offset == 1 for st in forward.stop_times if st.disposition == "stop")
        )
        midnight = self.reverse_by["23:45"]
        matiko = next(st for st in midnight.stop_times if st.stop_name == "Matiko-Bilbao")
        deba = next(st for st in midnight.stop_times if st.stop_name == "Deba")
        self.assertEqual(matiko.day_offset, 0)
        self.assertEqual(matiko.time, "23:45")
        self.assertEqual(deba.day_offset, 1)
        self.assertEqual(deba.time, "25:31")

    def test_no_stops_before_night_table(self):
        forward = self.forward_by["25:37"]
        pasaia = next(st for st in forward.stop_times if st.stop_name == "Pasaia")
        self.assertEqual(pasaia.disposition, "not_served")
        self.assertIsNone(pasaia.time)

    def test_monotonic_extended(self):
        for service in self.forward + self.reverse:
            minutes = [
                to_minutes(st.time) for st in service.stop_times if st.time and st.time != "?"
            ]
            self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
