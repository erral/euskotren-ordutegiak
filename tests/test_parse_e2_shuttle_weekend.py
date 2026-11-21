import unittest
from pathlib import Path

from euskotren_timetable.parse_e2_shuttle_weekend import (
    FORWARD_SATURDAY,
    FORWARD_SUNDAY,
    REVERSE_SATURDAY,
    REVERSE_SUNDAY,
    parse_e2_shuttle_block,
)

FORWARD = Path("data/pdfs/e2_t1_hendaia_lasarte.pdf")
REVERSE = Path("data/pdfs/e2_t1_lasarte_hendaia.pdf")


@unittest.skipUnless(FORWARD.exists() and REVERSE.exists(), "run the manifest first")
class ParseE2ShuttleWeekendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward_sa, cls.forward_sa_rules = parse_e2_shuttle_block(
            FORWARD, "test", FORWARD_SATURDAY
        )
        cls.forward_su, cls.forward_su_rules = parse_e2_shuttle_block(
            FORWARD, "test", FORWARD_SUNDAY
        )
        cls.reverse_sa, cls.reverse_sa_rules = parse_e2_shuttle_block(
            REVERSE, "test", REVERSE_SATURDAY
        )
        cls.reverse_su, cls.reverse_su_rules = parse_e2_shuttle_block(
            REVERSE, "test", REVERSE_SUNDAY
        )

    def test_counts(self):
        self.assertEqual(len(self.forward_sa), 126)
        self.assertEqual(len(self.forward_su), 108)
        self.assertEqual(len(self.reverse_sa), 128)
        self.assertEqual(len(self.reverse_su), 107)

    def test_first_last(self):
        self.assertEqual(self.forward_sa[0].departure, "6:35")
        self.assertEqual(self.forward_sa[-1].departure, "22:58")
        self.assertEqual(self.forward_su[0].departure, "6:35")
        self.assertEqual(self.forward_su[-1].departure, "22:58")
        self.assertEqual(self.reverse_sa[0].departure, "6:41")
        self.assertEqual(self.reverse_sa[-1].departure, "23:05")
        self.assertEqual(self.reverse_su[0].departure, "6:41")
        self.assertEqual(self.reverse_su[-1].departure, "23:05")

    def test_rules(self):
        forward_sa = {rule.rule_id: rule for rule in self.forward_sa_rules}
        self.assertEqual(
            len(forward_sa["E2-T1-PASAIA-ANORGA-SA-0658-2158-7.5"].expanded_service_ids), 121
        )
        forward_su = {rule.rule_id: rule for rule in self.forward_su_rules}
        self.assertEqual(
            len(forward_su["E2-T1-PASAIA-ANORGA-SU-0658-1258-60"].expanded_service_ids), 30
        )
        self.assertEqual(
            len(forward_su["E2-T1-PASAIA-ANORGA-SU-1258-2158-7.5"].expanded_service_ids), 73
        )
        reverse_sa = {rule.rule_id: rule for rule in self.reverse_sa_rules}
        self.assertEqual(
            len(reverse_sa["E2-T1-ANORGA-PASAIA-SA-0711-2241-7.5"].expanded_service_ids), 125
        )
        reverse_su = {rule.rule_id: rule for rule in self.reverse_su_rules}
        self.assertEqual(
            len(reverse_su["E2-T1-ANORGA-PASAIA-SU-0641-0826-15"].expanded_service_ids), 8
        )
        self.assertEqual(
            len(reverse_su["E2-T1-ANORGA-PASAIA-SU-0826-1341-60"].expanded_service_ids), 30
        )
        self.assertEqual(
            len(reverse_su["E2-T1-ANORGA-PASAIA-SU-1411-2241-7.5"].expanded_service_ids), 69
        )

    def test_template_rows(self):
        forward_sa = {service.departure: service for service in self.forward_sa}
        service = forward_sa["6:58"]
        self.assertEqual(len(service.stop_times), 11)
        self.assertEqual(service.stop_times[0].stop_name, "Pasaia")
        self.assertEqual(service.stop_times[-1].stop_name, "Añorga (Donostia)")
        self.assertEqual(service.stop_times[1].time, "7:00")

    def test_monotonic(self):
        for services in (
            self.forward_sa,
            self.forward_su,
            self.reverse_sa,
            self.reverse_su,
        ):
            for service in services:
                times = [st.time for st in service.stop_times if st.time and st.time != "?"]
                minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]
                self.assertEqual(minutes, sorted(minutes), service.service_id)


if __name__ == "__main__":
    unittest.main()
