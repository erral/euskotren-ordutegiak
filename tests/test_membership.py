import unittest
from pathlib import Path

from euskotren_timetable.corridors import CORRIDORS, assign_membership, services_for_corridor
from euskotren_timetable.parse_e1 import parse_e1_weekday
from euskotren_timetable.parse_e1_eibar import parse_e1_eibar
from euskotren_timetable.parse_e1_elgoibar import parse_e1_elgoibar
from euskotren_timetable.parse_e1_night import parse_e1_night, parse_e1_night_reverse
from euskotren_timetable.parse_e1_partial import (
    FORWARD_SATURDAY,
    FORWARD_SUNDAY,
    FORWARD_WEEKDAY,
    REVERSE_SATURDAY,
    REVERSE_SUNDAY,
    REVERSE_WEEKDAY,
    build_partial_services,
)
from euskotren_timetable.parse_e1_refuerzo import parse_e1_refuerzos
from euskotren_timetable.parse_e1_reverse import parse_e1_reverse
from euskotren_timetable.parse_e1_weekend import parse_e1_weekend, parse_e1_weekend_reverse
from euskotren_timetable.parse_e2 import parse_e2_reverse, parse_e2_weekday
from euskotren_timetable.parse_e2_shuttle_weekend import parse_e2_shuttle_weekend
from euskotren_timetable.parse_e2_weekend import parse_e2_weekend, parse_e2_weekend_reverse
from euskotren_timetable.parse_night import (
    parse_e2_night,
    parse_e2_night_reverse,
    parse_e4_night,
    parse_e4_night_reverse,
)
from euskotren_timetable.parse_e3 import (
    parse_e3_reverse,
    parse_e3_weekday,
    parse_e3_weekend,
    parse_e3_weekend_reverse,
)
from euskotren_timetable.parse_e4 import (
    GERNIKA_WD_FORWARD,
    GERNIKA_WD_REVERSE,
    GERNIKA_WE_FORWARD,
    GERNIKA_WE_REVERSE,
    parse_e4_gernika_turns,
    parse_e4_reverse,
    parse_e4_weekday,
    parse_e4_weekend,
    parse_e4_weekend_reverse,
)
from euskotren_timetable.parse_l3 import (
    parse_l3_reverse,
    parse_l3_weekday,
    parse_l3_weekend,
    parse_l3_weekend_reverse,
)
from euskotren_timetable.parse_l3_night import parse_e3_night, parse_l3_night

PDFS = {
    "e1w": Path("data/pdfs/e1_pasaia_matiko.pdf"),
    "e1e": Path("data/pdfs/e1_matiko_pasaia.pdf"),
    "e2w": Path("data/pdfs/e2_t1_hendaia_lasarte.pdf"),
    "e2e": Path("data/pdfs/e2_t1_lasarte_hendaia.pdf"),
    "e4": Path("data/pdfs/e4_bilbao_bermeo.pdf"),
    "e3": Path("data/pdfs/e3_l3.pdf"),
}


@unittest.skipUnless(all(path.exists() for path in PDFS.values()), "run the manifest first")
class MembershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        e1w, _ = parse_e1_weekday(PDFS["e1w"], "test")
        e1e, _ = parse_e1_reverse(PDFS["e1e"], "test")
        e1we, _ = parse_e1_weekend(PDFS["e1w"], "test")
        e1ww, _ = parse_e1_weekend_reverse(PDFS["e1e"], "test")
        e1snw = parse_e1_night(PDFS["e1w"], "test")
        e1sne = parse_e1_night_reverse(PDFS["e1e"], "test")
        e1r = parse_e1_refuerzos(PDFS["e1w"], PDFS["e1e"], "test", "test")
        e1elg = parse_e1_elgoibar(PDFS["e1w"], PDFS["e1e"], "test", "test")
        e1eib, _ = parse_e1_eibar(PDFS["e1w"], PDFS["e1e"], "test", "test")
        e1w_times = {service.departure for service in e1w}
        e1we_times = {service.departure for service in e1we}
        e1e_zumaia = {
            next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
            for service in e1e
        }
        e1ww_zumaia = {
            next(st.time for st in service.stop_times if st.stop_name == "Zumaia")
            for service in e1ww
        }
        e1p = (
            build_partial_services(PDFS["e1w"], "test", FORWARD_WEEKDAY, e1w_times, "Pasaia-Matiko", "PASAIA-ZUMAIA")
            + build_partial_services(PDFS["e1w"], "test", FORWARD_SATURDAY, e1we_times, "Pasaia-Matiko", "PASAIA-ZUMAIA")
            + build_partial_services(PDFS["e1w"], "test", FORWARD_SUNDAY, e1we_times, "Pasaia-Matiko", "PASAIA-ZUMAIA")
            + build_partial_services(PDFS["e1e"], "test", REVERSE_WEEKDAY, e1e_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA")
            + build_partial_services(PDFS["e1e"], "test", REVERSE_SATURDAY, e1ww_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA")
            + build_partial_services(PDFS["e1e"], "test", REVERSE_SUNDAY, e1ww_zumaia, "Matiko-Pasaia", "ZUMAIA-PASAIA")
        )
        e2w, _ = parse_e2_weekday(PDFS["e2w"], "test")
        e2e, _ = parse_e2_reverse(PDFS["e2e"], "test")
        e2we, _ = parse_e2_weekend(PDFS["e2w"], "test")
        e2ww, _ = parse_e2_weekend_reverse(PDFS["e2e"], "test")
        e2sh, _ = parse_e2_shuttle_weekend(PDFS["e2w"], PDFS["e2e"], "test", "test")
        e2snw = parse_e2_night(PDFS["e2w"], "test")
        e2sne = parse_e2_night_reverse(PDFS["e2e"], "test")
        e4snw = parse_e4_night(PDFS["e4"], "test")
        e4sne = parse_e4_night_reverse(PDFS["e4"], "test")
        e4e, _ = parse_e4_weekday(PDFS["e4"], "test")
        e4w, _ = parse_e4_reverse(PDFS["e4"], "test")
        e4we, _ = parse_e4_weekend(PDFS["e4"], "test")
        e4ww, _ = parse_e4_weekend_reverse(PDFS["e4"], "test")
        e4ger = (
            parse_e4_gernika_turns(PDFS["e4"], "test", GERNIKA_WD_FORWARD)
            + parse_e4_gernika_turns(PDFS["e4"], "test", GERNIKA_WE_FORWARD)
            + parse_e4_gernika_turns(PDFS["e4"], "test", GERNIKA_WD_REVERSE)
            + parse_e4_gernika_turns(PDFS["e4"], "test", GERNIKA_WE_REVERSE)
        )
        e3e, _ = parse_e3_weekday(PDFS["e3"], "test")
        e3w, _ = parse_e3_reverse(PDFS["e3"], "test")
        e3we, _ = parse_e3_weekend(PDFS["e3"], "test")
        e3ww, _ = parse_e3_weekend_reverse(PDFS["e3"], "test")
        l3e, _ = parse_l3_weekday(PDFS["e3"], "test")
        l3w, _ = parse_l3_reverse(PDFS["e3"], "test")
        l3we, _ = parse_l3_weekend(PDFS["e3"], "test")
        l3ww, _ = parse_l3_weekend_reverse(PDFS["e3"], "test")
        l3night, _ = parse_l3_night(PDFS["e3"], "test")
        e3night = parse_e3_night(PDFS["e3"], "test")
        cls.services = (
            e1w + e1e + e1we + e1ww + e1snw + e1sne + e1p + e1r + e1elg + e1eib
            + e2w + e2e + e2we + e2ww + e2sh
            + e2snw + e2sne
            + e4w + e4e + e4we + e4ww + e4ger + e4snw + e4sne
            + e3w + e3e + e3we + e3ww + e3night
            + l3w + l3e + l3we + l3ww + l3night
        )
        assign_membership(cls.services)
        cls.by_id = {service.service_id: service for service in cls.services}

    def test_allowed_corridors(self):
        allowed = {
            "Pasaia-Matiko": {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
            "Matiko-Pasaia": {"E1 Matiko-Pasaia", "E2-T1 Lasarte-Hendaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
            "Hendaia-Lasarte": {"E2-T1 Hendaia-Lasarte", "E1 Pasaia-Matiko"},
            "Lasarte-Hendaia": {"E2-T1 Lasarte-Hendaia", "E1 Matiko-Pasaia"},
            "Bermeo-Matiko": {"E4 Bermeo-Matiko", "E1 Pasaia-Matiko", "E3-L3 Kukullaga-Lezama"},
            "Matiko-Bermeo": {"E4 Matiko-Bermeo", "E1 Matiko-Pasaia", "E3-L3 Lezama-Kukullaga"},
            "Lezama-Kukullaga": {"E3-L3 Lezama-Kukullaga", "E1 Matiko-Pasaia", "E4 Matiko-Bermeo"},
            "Kukullaga-Lezama": {"E3-L3 Kukullaga-Lezama", "E1 Pasaia-Matiko", "E4 Bermeo-Matiko"},
            "Matiko-Kukullaga": {"E3-L3 Lezama-Kukullaga", "E1 Matiko-Pasaia", "E4 Matiko-Bermeo"},
            "Kukullaga-Matiko": {"E3-L3 Kukullaga-Lezama", "E1 Pasaia-Matiko", "E4 Bermeo-Matiko"},
        }
        primary = {
            "Pasaia-Matiko": "E1 Pasaia-Matiko",
            "Matiko-Pasaia": "E1 Matiko-Pasaia",
            "Hendaia-Lasarte": "E2-T1 Hendaia-Lasarte",
            "Lasarte-Hendaia": "E2-T1 Lasarte-Hendaia",
            "Bermeo-Matiko": "E4 Bermeo-Matiko",
            "Matiko-Bermeo": "E4 Matiko-Bermeo",
            "Lezama-Kukullaga": "E3-L3 Lezama-Kukullaga",
            "Kukullaga-Lezama": "E3-L3 Kukullaga-Lezama",
            "Matiko-Kukullaga": "E3-L3 Lezama-Kukullaga",
            "Kukullaga-Matiko": "E3-L3 Kukullaga-Lezama",
        }
        for service in self.services:
            self.assertTrue(set(service.appears_in) <= allowed[service.direction], service.service_id)
            self.assertIn(primary[service.direction], service.appears_in, service.service_id)

    def test_short_turn_membership(self):
        self.assertEqual(
            set(self.by_id["E1-PASAIA-MATIKO-WD-0535"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E1-PASAIA-MATIKO-WD-2035"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"},
        )
        self.assertEqual(
            set(self.by_id["E4-BERMEO-MATIKO-WD-0618"].appears_in),
            {"E4 Bermeo-Matiko", "E1 Pasaia-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E4-BERMEO-MATIKO-WD-2235"].appears_in),
            {"E4 Bermeo-Matiko"},
        )
        self.assertEqual(
            set(self.by_id["E3-L3-LEZAMA-KUKULLAGA-WD-0637"].appears_in),
            {"E3-L3 Lezama-Kukullaga", "E1 Matiko-Pasaia", "E4 Matiko-Bermeo"},
        )

    def test_shuttle_membership(self):
        self.assertEqual(
            set(self.by_id["E2-T1-PASAIA-ANORGA-SA-0658"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"},
        )
        self.assertEqual(
            set(self.by_id["E2-T1-ANORGA-PASAIA-SA-0711"].appears_in),
            {"E1 Matiko-Pasaia", "E2-T1 Lasarte-Hendaia"},
        )
        self.assertEqual(
            set(self.by_id["E2-T1-PASAIA-ANORGA-SU-0658"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"},
        )
        self.assertEqual(
            set(self.by_id["E2-T1-ANORGA-PASAIA-SU-0641"].appears_in),
            {"E1 Matiko-Pasaia", "E2-T1 Lasarte-Hendaia"},
        )

    def test_night_membership(self):
        self.assertEqual(
            set(self.by_id["E1-PASAIA-MATIKO-SN-2537"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E1-MATIKO-PASAIA-SN-2345"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )

    def test_e2_e4_night_membership(self):
        self.assertEqual(
            set(self.by_id["E2-T1-HENDAIA-LASARTE-SN-2304"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"},
        )
        self.assertEqual(
            set(self.by_id["E2-T1-LASARTE-HENDAIA-SN-2305"].appears_in),
            {"E1 Matiko-Pasaia", "E2-T1 Lasarte-Hendaia"},
        )
        self.assertEqual(
            set(self.by_id["E4-MATIKO-BERMEO-SN-2212"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )
        self.assertEqual(
            set(self.by_id["E4-BERMEO-MATIKO-SN-2334"].appears_in),
            {"E4 Bermeo-Matiko"},
        )

    def test_l3_night_membership(self):
        self.assertEqual(
            set(self.by_id["E3-L3-MATIKO-KUKULLAGA-FN-2330"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )
        self.assertEqual(
            set(self.by_id["E3-L3-KUKULLAGA-MATIKO-SN-2338"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E3-L3-LEZAMA-KUKULLAGA-SN-2307"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )
        self.assertEqual(
            set(self.by_id["E3-L3-KUKULLAGA-LEZAMA-SN-2254"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )

    def test_e4_weekend_specials(self):
        self.assertEqual(
            set(self.by_id["E4-MATIKO-BERMEO-SU-2212"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )
        self.assertEqual(
            set(self.by_id["E4-MATIKO-BERMEO-WE-2252"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )
        self.assertEqual(
            set(self.by_id["E4-BERMEO-MATIKO-WE-2245"].appears_in),
            {"E4 Bermeo-Matiko"},
        )

    def test_e1_partial_membership(self):
        self.assertEqual(
            set(self.by_id["E1-PASAIA-ZUMAIA-WD-0605"].appears_in),
            {"E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"},
        )
        self.assertEqual(
            set(self.by_id["E1-ZUMAIA-PASAIA-WD-0600"].appears_in),
            {"E1 Matiko-Pasaia", "E2-T1 Lasarte-Hendaia"},
        )

    def test_refuerzo_membership(self):
        self.assertEqual(
            set(self.by_id["E1-ZALDIBAR-MATIKO-WD-0712"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E1-MATIKO-TRANA-WD-0832"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )

    def test_elgoibar_membership(self):
        self.assertEqual(
            set(self.by_id["E1-ELGOIBAR-MATIKO-WD-0701"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )
        self.assertEqual(
            set(self.by_id["E1-MATIKO-ELGOIBAR-WD-0555"].appears_in),
            {"E1 Matiko-Pasaia", "E4 Matiko-Bermeo", "E3-L3 Lezama-Kukullaga"},
        )

    def test_eibar_membership(self):
        self.assertEqual(
            set(self.by_id["E1-EIBAR-ERMUA-WD-0611"].appears_in),
            {"E1 Pasaia-Matiko"},
        )
        self.assertEqual(
            set(self.by_id["E1-ERMUA-EIBAR-WD-0601"].appears_in),
            {"E1 Matiko-Pasaia"},
        )

    def test_gernika_short_turn_membership(self):
        self.assertEqual(
            set(self.by_id["E4-MATIKO-BERMEO-WD-0552"].appears_in),
            {"E4 Matiko-Bermeo"},
        )
        self.assertEqual(
            set(self.by_id["E4-BERMEO-MATIKO-WD-0615"].appears_in),
            {"E1 Pasaia-Matiko", "E4 Bermeo-Matiko", "E3-L3 Kukullaga-Lezama"},
        )

    def test_corridor_counts(self):
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[0])), 1110)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[1])), 1108)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[2])), 524)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[3])), 522)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[4])), 514)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[5])), 509)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[6])), 509)
        self.assertEqual(len(services_for_corridor(self.services, CORRIDORS[7])), 505)


if __name__ == "__main__":
    unittest.main()
