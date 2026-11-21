import unittest

from euskotren_timetable.stops import (
    E1_FULL_42,
    E1_PARTIAL_17,
    E1_STOPS,
    E1_TOP0_MISSING,
    E2_STOPS,
    E3L3_STOPS,
    E4_STOPS,
    STOP_REGISTRY,
    stop_id,
)


class StopTests(unittest.TestCase):
    def test_line_counts(self):
        self.assertEqual(len(E1_STOPS), 50)
        self.assertEqual(len(E2_STOPS), 23)
        self.assertEqual(len(E3L3_STOPS), 16)
        self.assertEqual(len(E4_STOPS), 25)

    def test_e1_table_columns(self):
        self.assertEqual(len(E1_FULL_42), 42)
        self.assertEqual(len(E1_PARTIAL_17), 17)
        self.assertEqual(len(E1_TOP0_MISSING), 8)

    def test_shared_stop_ids(self):
        self.assertEqual(stop_id("Pasaia"), stop_id("Pasaia"))
        self.assertEqual(stop_id("Matiko-Bilbao"), stop_id("Matiko-Bilbao"))

    def test_distinct_amorebieta_stops(self):
        self.assertNotEqual(stop_id("Amorebieta Geltokia"), stop_id("Amorebieta Geralekua"))

    def test_no_city_entity(self):
        self.assertNotIn("City", STOP_REGISTRY)




if __name__ == "__main__":
    unittest.main()
