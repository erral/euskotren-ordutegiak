import unittest

from euskotren_timetable.service_order import (
    CALENDAR_ORDER,
    DIRECTION_ORDER,
    LINE_ORDER,
    corridor_sort_key,
    master_sort_key,
)
from tests.support import make_service


class ServiceOrderTests(unittest.TestCase):
    def test_calendar_order(self):
        self.assertEqual(list(CALENDAR_ORDER), ["WD", "SA", "SU", "WE", "FN", "SN"])

    def test_line_order(self):
        self.assertEqual(list(LINE_ORDER), ["E1", "E2-T1", "E4", "E3-L3"])

    def test_direction_order(self):
        self.assertEqual(DIRECTION_ORDER["E1"], ("Pasaia-Matiko", "Matiko-Pasaia"))
        self.assertEqual(DIRECTION_ORDER["E2-T1"], ("Hendaia-Lasarte", "Lasarte-Hendaia"))
        self.assertEqual(DIRECTION_ORDER["E4"], ("Matiko-Bermeo", "Bermeo-Matiko"))
        self.assertEqual(
            DIRECTION_ORDER["E3-L3"],
            (
                "Lezama-Kukullaga",
                "Kukullaga-Lezama",
                "Matiko-Kukullaga",
                "Kukullaga-Matiko",
            ),
        )

    def test_e3_l3_l3_local_follows_branch(self):
        branch = make_service("BRANCH", "WD", "E3-L3", "Lezama-Kukullaga", "5:36")
        local = make_service("LOCAL", "WD", "E3-L3", "Matiko-Kukullaga", "5:36")
        ordered = sorted([local, branch], key=master_sort_key)
        self.assertEqual([s.service_id for s in ordered], ["BRANCH", "LOCAL"])

    def test_master_key_sorts_calendar_first(self):
        weekday_e1 = make_service("A", "WD", "E1", "Pasaia-Matiko", "5:35")
        weekday_e2 = make_service("B", "WD", "E2-T1", "Hendaia-Lasarte", "5:35")
        weekend_e1 = make_service("C", "WE", "E1", "Pasaia-Matiko", "8:00")
        ordered = sorted([weekend_e1, weekday_e2, weekday_e1], key=master_sort_key)
        self.assertEqual([s.service_id for s in ordered], ["A", "B", "C"])

    def test_master_key_line_order(self):
        e4 = make_service("E4-SERVICE", "WD", "E4", "Matiko-Bermeo", "10:00")
        e3 = make_service("E3-SERVICE", "WD", "E3-L3", "Lezama-Kukullaga", "10:00")
        ordered = sorted([e3, e4], key=master_sort_key)
        self.assertEqual([s.service_id for s in ordered], ["E4-SERVICE", "E3-SERVICE"])

    def test_master_key_service_id_tiebreak(self):
        first = make_service("A-SERVICE", "WD", "E1", "Pasaia-Matiko", "5:35")
        second = make_service("B-SERVICE", "WD", "E1", "Pasaia-Matiko", "5:35")
        ordered = sorted([second, first], key=master_sort_key)
        self.assertEqual([s.service_id for s in ordered], ["A-SERVICE", "B-SERVICE"])

    def test_corridor_own_line_first_at_equal_departure(self):
        e1 = make_service("E1-SERVICE", "WD", "E1", "Pasaia-Matiko", "5:35")
        e2 = make_service("E2-SERVICE", "WD", "E2-T1", "Hendaia-Lasarte", "5:35")
        in_e1 = sorted([e2, e1], key=lambda s: corridor_sort_key(s, "E1"))
        in_e2 = sorted([e1, e2], key=lambda s: corridor_sort_key(s, "E2-T1"))
        self.assertEqual([s.service_id for s in in_e1], ["E1-SERVICE", "E2-SERVICE"])
        self.assertEqual([s.service_id for s in in_e2], ["E2-SERVICE", "E1-SERVICE"])

    def test_corridor_departure_beats_own_line(self):
        early_cross_line = make_service(
            "E2-EARLY", "WD", "E2-T1", "Hendaia-Lasarte", "5:28"
        )
        later_own_line = make_service(
            "E1-LATER", "WD", "E1", "Pasaia-Matiko", "5:35"
        )
        ordered = sorted(
            [later_own_line, early_cross_line],
            key=lambda s: corridor_sort_key(s, "E1"),
        )
        self.assertEqual([s.service_id for s in ordered], ["E2-EARLY", "E1-LATER"])

    def test_night_uses_extended_clock(self):
        late = make_service("LATE", "SN", "E1", "Matiko-Pasaia", "25:37")
        midnight = make_service("MID", "SN", "E1", "Matiko-Pasaia", "24:00")
        before = make_service("BEFORE", "SN", "E1", "Matiko-Pasaia", "23:45")
        ordered = sorted([late, midnight, before], key=master_sort_key)
        self.assertEqual([s.service_id for s in ordered], ["BEFORE", "MID", "LATE"])

    def test_unknown_calendar_raises(self):
        service = make_service("BAD", "XX", "E1", "Pasaia-Matiko", "5:35")
        with self.assertRaises(ValueError):
            master_sort_key(service)

    def test_unknown_line_raises(self):
        service = make_service("BAD", "WD", "E9", "Pasaia-Matiko", "5:35")
        with self.assertRaises(ValueError):
            master_sort_key(service)

    def test_unknown_direction_raises(self):
        service = make_service("BAD", "WD", "E1", "Wrong-Direction", "5:35")
        with self.assertRaises(ValueError):
            master_sort_key(service)

    def test_missing_departure_raises(self):
        service = make_service("BAD", "WD", "E1", "Pasaia-Matiko", "5:35")
        service.departure = ""
        with self.assertRaises(ValueError):
            master_sort_key(service)


if __name__ == "__main__":
    unittest.main()
