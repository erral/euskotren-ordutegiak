"""Structural checks for the E1/E2 weekday slice in both directions."""

import re
from dataclasses import dataclass

from collections import Counter

from .corridors import CORRIDORS, appears_in as corridor_appears_in
from .model import FrequencyRule, Service
from .parse_e1 import ALTZOLA, is_time, to_minutes
from .service_order import master_sort_key
from .stops import STOP_REGISTRY

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")


@dataclass
class Check:
    name: str
    status: str
    detail: str


def _check(name: str, ok: bool, detail: str) -> Check:
    return Check(name, "PASS" if ok else "FAIL", detail)


def _first_last(services: list[Service], first: str, last: str, name: str) -> Check:
    if not services:
        return _check(name, False, "no services")
    return _check(name, services[0].departure == first and services[-1].departure == last,
                  f"{services[0].departure} .. {services[-1].departure}")


def _complete(service: Service | None, expected: int, expected_unpublished: int, name: str) -> Check:
    if service is None:
        return _check(name, False, "service missing")
    unpublished = [st for st in service.stop_times if st.disposition == "unpublished"]
    return _check(
        name,
        len(service.stop_times) == expected and len(unpublished) == expected_unpublished,
        f"{len(service.stop_times)} stops, unpublished={len(unpublished)}",
    )


def _stop_time(
    service: Service | None, stop_name: str, expected: str, name: str
) -> Check:
    if service is None:
        return _check(name, False, "service missing")
    actual = next(
        (st.time for st in service.stop_times if st.stop_name == stop_name), None
    )
    return _check(name, actual == expected, f"expected {expected}, got {actual}")


def _day_offset(
    service: Service | None, stop_name: str, expected: int, name: str
) -> Check:
    if service is None:
        return _check(name, False, "service missing")
    actual = next(
        (st.day_offset for st in service.stop_times if st.stop_name == stop_name), None
    )
    return _check(name, actual == expected, f"expected {expected}, got {actual}")


def _altzola(service: Service | None, expected: str | None, name: str) -> Check:
    actual = None
    if service:
        actual = next((st.time for st in service.stop_times if st.stop_name == ALTZOLA), None)
    return _check(name, actual == expected, f"expected {expected}, got {actual}")


def validate(services: list[Service], rules: list[FrequencyRule]) -> list[Check]:
    checks: list[Check] = []

    e1_elgoibar = [s for s in services if s.service_id.startswith(("E1-ELGOIBAR-MATIKO", "E1-MATIKO-ELGOIBAR"))]
    e1_eibar = [s for s in services if s.service_id.startswith(("E1-EIBAR-ERMUA", "E1-ERMUA-EIBAR"))]
    partial_ids = {s.service_id for s in e1_elgoibar + e1_eibar}
    e1w = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "WD" and s.destination != "Zumaia" and "refuerzo" not in s.pattern and s.service_id not in partial_ids]
    e1e = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "WD" and s.origin != "Zumaia" and "refuerzo" not in s.pattern and s.service_id not in partial_ids]
    e1we = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "WE" and s.destination != "Zumaia" and "refuerzo" not in s.pattern and s.service_id not in partial_ids]
    e1ww = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "WE" and s.origin != "Zumaia" and "refuerzo" not in s.pattern and s.service_id not in partial_ids]
    e1elg_wd = [s for s in e1_elgoibar if s.calendar == "WD" and s.direction == "Pasaia-Matiko"]
    e1elg_we = [s for s in e1_elgoibar if s.calendar == "WE" and s.direction == "Pasaia-Matiko"]
    e1elgr_wd = [s for s in e1_elgoibar if s.calendar == "WD" and s.direction == "Matiko-Pasaia"]
    e1elgr_we = [s for s in e1_elgoibar if s.calendar == "WE" and s.direction == "Matiko-Pasaia"]
    e1eib_wd = [s for s in e1_eibar if s.calendar == "WD" and s.direction == "Pasaia-Matiko"]
    e1eib_we = [s for s in e1_eibar if s.calendar == "WE" and s.direction == "Pasaia-Matiko"]
    e1eibr_wd = [s for s in e1_eibar if s.calendar == "WD" and s.direction == "Matiko-Pasaia"]
    e1eibr_we = [s for s in e1_eibar if s.calendar == "WE" and s.direction == "Matiko-Pasaia"]
    e1_ref = [s for s in services if s.primary_line == "E1" and s.calendar == "WD" and "refuerzo" in s.pattern]
    e1_ref_fwd = [s for s in e1_ref if s.direction == "Pasaia-Matiko"]
    e1_ref_rev = [s for s in e1_ref if s.direction == "Matiko-Pasaia"]
    e1_ref_fwd_by = {s.departure: s for s in e1_ref_fwd}
    e1_ref_rev_by = {s.departure: s for s in e1_ref_rev}
    e1p_wd = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "WD" and s.destination == "Zumaia"]
    e1p_sa = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "SA" and s.destination == "Zumaia"]
    e1p_su = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "SU" and s.destination == "Zumaia"]
    e1pr_wd = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "WD" and s.origin == "Zumaia"]
    e1pr_sa = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "SA" and s.origin == "Zumaia"]
    e1pr_su = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "SU" and s.origin == "Zumaia"]
    e1snw = [s for s in services if s.primary_line == "E1" and s.direction == "Pasaia-Matiko" and s.calendar == "SN"]
    e1sne = [s for s in services if s.primary_line == "E1" and s.direction == "Matiko-Pasaia" and s.calendar == "SN"]
    e2w = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Hendaia-Lasarte" and s.calendar == "WD"]
    e2e = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Lasarte-Hendaia" and s.calendar == "WD"]
    e2we = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Hendaia-Lasarte" and s.calendar == "WE"]
    e2ww = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Lasarte-Hendaia" and s.calendar == "WE"]
    e2sa = [s for s in services if s.primary_line == "E2-T1" and s.calendar == "SA"]
    e2su = [s for s in services if s.primary_line == "E2-T1" and s.calendar == "SU"]
    e2snw = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Hendaia-Lasarte" and s.calendar == "SN"]
    e2sne = [s for s in services if s.primary_line == "E2-T1" and s.direction == "Lasarte-Hendaia" and s.calendar == "SN"]
    e2w_full = [s for s in e2w if s.origin == "Hendaia"]
    e2w_partial = [s for s in e2w if s.origin == "Pasaia"]
    e2e_full = [s for s in e2e if s.origin == "Lasarte-Oria"]
    e2e_partial = [s for s in e2e if s.origin == "Añorga (Donostia)"]
    e4e = [s for s in services if s.primary_line == "E4" and s.direction == "Matiko-Bermeo" and s.calendar == "WD" and s.origin != "Gernika"]
    e4w = [s for s in services if s.primary_line == "E4" and s.direction == "Bermeo-Matiko" and s.calendar == "WD" and s.origin != "Gernika"]
    e4we = [s for s in services if s.primary_line == "E4" and s.direction == "Matiko-Bermeo" and s.calendar == "WE" and s.origin != "Gernika"]
    e4su = [s for s in services if s.primary_line == "E4" and s.direction == "Matiko-Bermeo" and s.calendar == "SU"]
    e4ww = [s for s in services if s.primary_line == "E4" and s.direction == "Bermeo-Matiko" and s.calendar == "WE" and s.origin != "Gernika"]
    e4snw = [s for s in services if s.primary_line == "E4" and s.direction == "Matiko-Bermeo" and s.calendar == "SN"]
    e4sne = [s for s in services if s.primary_line == "E4" and s.direction == "Bermeo-Matiko" and s.calendar == "SN"]
    e4ger_wd = [s for s in services if s.primary_line == "E4" and s.origin == "Gernika" and s.calendar == "WD"]
    e4ger_we = [s for s in services if s.primary_line == "E4" and s.origin == "Gernika" and s.calendar == "WE"]
    e3e = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Lezama-Kukullaga" and s.calendar == "WD"]
    e3w = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Lezama" and s.calendar == "WD"]
    e3we = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Lezama-Kukullaga" and s.calendar == "WE"]
    e3ww = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Lezama" and s.calendar == "WE"]
    l3e = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Matiko-Kukullaga" and s.calendar == "WD"]
    l3w = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Matiko" and s.calendar == "WD"]
    l3we = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Matiko-Kukullaga" and s.calendar == "WE"]
    l3ww = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Matiko" and s.calendar == "WE"]
    l3fn = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Matiko-Kukullaga" and s.calendar == "FN"]
    l3sn = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Matiko-Kukullaga" and s.calendar == "SN"]
    l3fnr = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Matiko" and s.calendar == "FN"]
    l3snr = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Matiko" and s.calendar == "SN"]
    e3sn = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Lezama-Kukullaga" and s.calendar == "SN"]
    e3snr = [s for s in services if s.primary_line == "E3-L3" and s.direction == "Kukullaga-Lezama" and s.calendar == "SN"]

    checks.append(_check("e1_west_count", len(e1w) == 16, f"found {len(e1w)}, expected 16"))
    checks.append(_check("e1_east_count", len(e1e) == 15, f"found {len(e1e)}, expected 15"))
    checks.append(_check("e1_weekend_west_count", len(e1we) == 14, f"found {len(e1we)}, expected 14"))
    checks.append(_check("e1_weekend_east_count", len(e1ww) == 14, f"found {len(e1ww)}, expected 14"))
    checks.append(_check("e1_saturday_night_west_count", len(e1snw) == 4, f"found {len(e1snw)}, expected 4"))
    checks.append(_check("e1_saturday_night_east_count", len(e1sne) == 4, f"found {len(e1sne)}, expected 4"))
    checks.append(_check("e1_partial_west_weekday_count", len(e1p_wd) == 17, f"found {len(e1p_wd)}, expected 17"))
    checks.append(_check("e1_partial_west_saturday_count", len(e1p_sa) == 17, f"found {len(e1p_sa)}, expected 17"))
    checks.append(_check("e1_partial_west_sunday_count", len(e1p_su) == 11, f"found {len(e1p_su)}, expected 11"))
    checks.append(_check("e1_partial_east_weekday_count", len(e1pr_wd) == 19, f"found {len(e1pr_wd)}, expected 19"))
    checks.append(_check("e1_partial_east_saturday_count", len(e1pr_sa) == 18, f"found {len(e1pr_sa)}, expected 18"))
    checks.append(_check("e1_partial_east_sunday_count", len(e1pr_su) == 10, f"found {len(e1pr_su)}, expected 10"))
    checks.append(_check("e1_refuerzo_count", len(e1_ref) == 5, f"found {len(e1_ref)}, expected 5"))
    checks.append(_check("e1_elgoibar_weekday_west_count", len(e1elg_wd) == 26, f"found {len(e1elg_wd)}, expected 26"))
    checks.append(_check("e1_elgoibar_weekend_west_count", len(e1elg_we) == 14, f"found {len(e1elg_we)}, expected 14"))
    checks.append(_check("e1_elgoibar_weekday_east_count", len(e1elgr_wd) == 25, f"found {len(e1elgr_wd)}, expected 25"))
    checks.append(_check("e1_elgoibar_weekend_east_count", len(e1elgr_we) == 14, f"found {len(e1elgr_we)}, expected 14"))
    checks.append(_check("e1_eibar_weekday_west_count", len(e1eib_wd) == 64, f"found {len(e1eib_wd)}, expected 64"))
    checks.append(_check("e1_eibar_weekend_west_count", len(e1eib_we) == 44, f"found {len(e1eib_we)}, expected 44"))
    checks.append(_check("e1_eibar_weekday_east_count", len(e1eibr_wd) == 63, f"found {len(e1eibr_wd)}, expected 63"))
    checks.append(_check("e1_eibar_weekend_east_count", len(e1eibr_we) == 43, f"found {len(e1eibr_we)}, expected 43"))
    checks.append(_check("e2_west_full_count", len(e2w_full) == 35, f"found {len(e2w_full)}, expected 35"))
    checks.append(_check("e2_west_partial_count", len(e2w_partial) == 139, f"found {len(e2w_partial)}, expected 139"))
    checks.append(_check("e2_weekend_west_count", len(e2ww) == 33, f"found {len(e2ww)}, expected 33"))
    checks.append(_check("e2_weekend_east_count", len(e2we) == 33, f"found {len(e2we)}, expected 33"))
    checks.append(_check("e2_east_full_count", len(e2e_full) == 34, f"found {len(e2e_full)}, expected 34"))
    checks.append(_check("e2_east_partial_count", len(e2e_partial) == 136, f"found {len(e2e_partial)}, expected 136"))
    checks.append(_check("e2_saturday_shuttle_count", len(e2sa) == 254, f"found {len(e2sa)}, expected 254"))
    checks.append(_check("e2_sunday_shuttle_count", len(e2su) == 215, f"found {len(e2su)}, expected 215"))
    checks.append(_check("e2_saturday_night_west_count", len(e2snw) == 8, f"found {len(e2snw)}, expected 8"))
    checks.append(_check("e2_saturday_night_east_count", len(e2sne) == 8, f"found {len(e2sne)}, expected 8"))
    checks.append(_check("e4_west_count", len(e4w) == 32, f"found {len(e4w)}, expected 32"))
    checks.append(_check("e4_east_count", len(e4e) == 33, f"found {len(e4e)}, expected 33"))
    checks.append(_check("e4_weekend_west_count", len(e4ww) == 16, f"found {len(e4ww)}, expected 16"))
    checks.append(_check("e4_weekend_east_count", len(e4we) == 15, f"found {len(e4we)}, expected 15"))
    checks.append(_check("e4_sunday_variant_count", len(e4su) == 1, f"found {len(e4su)}, expected 1"))
    checks.append(_check("e4_saturday_night_west_count", len(e4snw) == 5, f"found {len(e4snw)}, expected 5"))
    checks.append(_check("e4_saturday_night_east_count", len(e4sne) == 5, f"found {len(e4sne)}, expected 5"))
    checks.append(_check("e4_gernika_weekday_count", len(e4ger_wd) == 4, f"found {len(e4ger_wd)}, expected 4"))
    checks.append(_check("e4_gernika_weekend_count", len(e4ger_we) == 3, f"found {len(e4ger_we)}, expected 3"))
    checks.append(_check("e3_west_count", len(e3w) == 64, f"found {len(e3w)}, expected 64"))
    checks.append(_check("e3_east_count", len(e3e) == 62, f"found {len(e3e)}, expected 62"))
    checks.append(_check("e3_weekend_west_count", len(e3ww) == 31, f"found {len(e3ww)}, expected 31"))
    checks.append(_check("e3_weekend_east_count", len(e3we) == 32, f"found {len(e3we)}, expected 32"))
    checks.append(_check("l3_west_count", len(l3w) == 140, f"found {len(l3w)}, expected 140"))
    checks.append(_check("l3_east_count", len(l3e) == 138, f"found {len(l3e)}, expected 138"))
    checks.append(_check("l3_weekend_west_count", len(l3ww) == 103, f"found {len(l3ww)}, expected 103"))
    checks.append(_check("l3_weekend_east_count", len(l3we) == 101, f"found {len(l3we)}, expected 101"))
    invalid_departures = [
        service.service_id
        for service in services
        if not service.departure or not TIME_RE.match(service.departure)
    ]
    checks.append(
        _check(
            "service_departures_present",
            not invalid_departures,
            f"{len(invalid_departures)} missing or invalid departures",
        )
    )

    duplicate_ids = [
        service_id
        for service_id, count in Counter(service.service_id for service in services).items()
        if count > 1
    ]
    checks.append(
        _check(
            "service_ids_unique",
            not duplicate_ids,
            f"{len(duplicate_ids)} duplicate service IDs",
        )
    )

    invalid_sort_values = []
    for service in services:
        try:
            master_sort_key(service)
        except ValueError as exc:
            invalid_sort_values.append(f"{service.service_id}: {exc}")
    checks.append(
        _check(
            "service_sort_values",
            not invalid_sort_values,
            f"{len(invalid_sort_values)} invalid: {'; '.join(invalid_sort_values[:3])}",
        )
    )
    checks.append(_check("l3_friday_night_west_count", len(l3fn) == 14, f"found {len(l3fn)}, expected 14"))
    checks.append(_check("l3_saturday_night_west_count", len(l3sn) == 27, f"found {len(l3sn)}, expected 27"))
    checks.append(_check("l3_friday_night_east_count", len(l3fnr) == 12, f"found {len(l3fnr)}, expected 12"))
    checks.append(_check("l3_saturday_night_east_count", len(l3snr) == 26, f"found {len(l3snr)}, expected 26"))
    checks.append(_check("e3_saturday_night_west_count", len(e3sn) == 6, f"found {len(e3sn)}, expected 6"))
    checks.append(_check("e3_saturday_night_east_count", len(e3snr) == 5, f"found {len(e3snr)}, expected 5"))

    checks.append(_first_last(e1w, "5:35", "20:35", "e1_west_first_last"))
    checks.append(_first_last(e1e, "5:55", "19:55", "e1_east_first_last"))
    checks.append(_first_last(e1we, "7:35", "20:35", "e1_weekend_west_first_last"))
    checks.append(_first_last(e1ww, "6:52", "19:52", "e1_weekend_east_first_last"))
    checks.append(_first_last(e1snw, "25:37", "31:19", "e1_saturday_night_west_first_last"))
    checks.append(_first_last(e1sne, "23:45", "29:45", "e1_saturday_night_east_first_last"))
    checks.append(_first_last(e1p_wd, "6:05", "21:35", "e1_partial_west_weekday_first_last"))
    checks.append(_first_last(e1p_sa, "6:35", "21:35", "e1_partial_west_saturday_first_last"))
    checks.append(_first_last(e1p_su, "6:35", "21:35", "e1_partial_west_sunday_first_last"))
    checks.append(_first_last(e1pr_wd, "6:00", "22:31", "e1_partial_east_weekday_first_last"))
    checks.append(_first_last(e1pr_sa, "7:00", "22:31", "e1_partial_east_saturday_first_last"))
    checks.append(_first_last(e1pr_su, "8:00", "22:31", "e1_partial_east_sunday_first_last"))
    checks.append(_first_last(e1_ref_fwd, "6:42", "7:12", "e1_refuerzo_west_first_last"))
    checks.append(_first_last(e1_ref_rev, "7:32", "8:32", "e1_refuerzo_east_first_last"))
    checks.append(_first_last(e1elg_wd, "7:01", "22:01", "e1_elgoibar_weekday_west_first_last"))
    checks.append(_first_last(e1elg_we, "9:01", "22:01", "e1_elgoibar_weekend_west_first_last"))
    checks.append(_first_last(e1elgr_wd, "5:55", "19:55", "e1_elgoibar_weekday_east_first_last"))
    checks.append(_first_last(e1elgr_we, "6:52", "19:52", "e1_elgoibar_weekend_east_first_last"))
    checks.append(_first_last(e1eib_wd, "6:11", "22:11", "e1_eibar_weekday_west_first_last"))
    checks.append(_first_last(e1eib_we, "8:00", "22:11", "e1_eibar_weekend_west_first_last"))
    checks.append(_first_last(e1eibr_wd, "6:01", "22:01", "e1_eibar_weekday_east_first_last"))
    checks.append(_first_last(e1eibr_we, "8:01", "22:02", "e1_eibar_weekend_east_first_last"))
    checks.append(_check(
        "e1_refuerzo_zaldibar_destination",
        e1_ref_fwd_by.get("7:12") is not None and e1_ref_fwd_by["7:12"].destination == "Matiko-Bilbao",
        "Zaldibar refuerzo should reach Matiko",
    ))
    checks.append(_check(
        "e1_refuerzo_trana_destination",
        e1_ref_rev_by.get("8:32") is not None and e1_ref_rev_by["8:32"].destination == "Traña Abadiño",
        "08:32 refuerzo should reach Traña",
    ))
    checks.append(_first_last(e2w_full, "5:34", "22:34", "e2_west_full_first_last"))
    checks.append(_first_last(e2w_partial, "5:28", "22:58", "e2_west_partial_first_last"))
    checks.append(_first_last(e2we, "6:34", "22:34", "e2_weekend_east_first_last"))
    checks.append(_first_last(e2ww, "6:35", "22:35", "e2_weekend_west_first_last"))
    checks.append(_first_last(e2sa, "6:35", "23:05", "e2_saturday_shuttle_first_last"))
    checks.append(_first_last(e2su, "6:35", "23:05", "e2_sunday_shuttle_first_last"))
    checks.append(_first_last(e2snw, "23:04", "26:34", "e2_saturday_night_west_first_last"))
    checks.append(_first_last(e2sne, "23:05", "26:35", "e2_saturday_night_east_first_last"))
    checks.append(_first_last(e4snw, "22:12", "29:45", "e4_saturday_night_west_first_last"))
    checks.append(_first_last(e4sne, "23:34", "31:25", "e4_saturday_night_east_first_last"))
    checks.append(_first_last(e4ger_wd, "5:52", "6:41", "e4_gernika_weekday_first_last"))
    checks.append(_first_last(e4ger_we, "7:10", "8:19", "e4_gernika_weekend_first_last"))
    checks.append(_first_last(e2e_full, "6:05", "22:35", "e2_east_full_first_last"))
    checks.append(_first_last(e2e_partial, "5:41", "23:05", "e2_east_partial_first_last"))
    checks.append(_first_last(e4w, "6:18", "22:35", "e4_west_first_last"))
    checks.append(_first_last(e4e, "6:10", "22:10", "e4_east_first_last"))
    checks.append(_first_last(e4ww, "7:47", "22:45", "e4_weekend_west_first_last"))
    checks.append(_first_last(e4we, "8:22", "22:52", "e4_weekend_east_first_last"))
    checks.append(_first_last(e3w, "5:36", "22:59", "e3_west_first_last"))
    checks.append(_first_last(e3e, "6:07", "22:52", "e3_east_first_last"))
    checks.append(_first_last(e3ww, "7:24", "22:24", "e3_weekend_west_first_last"))
    checks.append(_first_last(e3we, "7:37", "23:07", "e3_weekend_east_first_last"))
    checks.append(_first_last(l3w, "5:36", "23:14", "l3_west_first_last"))
    checks.append(_first_last(l3e, "5:55", "23:02", "l3_east_first_last"))
    checks.append(_first_last(l3ww, "6:08", "23:17", "l3_weekend_west_first_last"))
    checks.append(_first_last(l3we, "6:00", "23:02", "l3_weekend_east_first_last"))
    checks.append(_first_last(l3fn, "23:12", "26:15", "l3_friday_night_west_first_last"))
    checks.append(_first_last(l3sn, "23:18", "29:45", "l3_saturday_night_west_first_last"))
    checks.append(_first_last(l3fnr, "23:24", "26:08", "l3_friday_night_east_first_last"))
    checks.append(_first_last(l3snr, "23:38", "29:53", "l3_saturday_night_east_first_last"))
    checks.append(_first_last(e3sn, "23:07", "30:57", "e3_saturday_night_west_first_last"))
    checks.append(_first_last(e3snr, "22:54", "30:08", "e3_saturday_night_east_first_last"))

    e1w_by = {s.departure: s for s in e1w}
    e1e_by = {s.departure: s for s in e1e}
    e1we_by = {s.departure: s for s in e1we}
    e1ww_by = {s.departure: s for s in e1ww}
    e1snw_by = {s.departure: s for s in e1snw}
    e1sne_by = {s.departure: s for s in e1sne}
    e2w_full_by = {s.departure: s for s in e2w_full}
    e2w_partial_by = {s.departure: s for s in e2w_partial}
    e2we_by = {s.departure: s for s in e2we}
    e2ww_by = {s.departure: s for s in e2ww}
    e2e_full_by = {s.departure: s for s in e2e_full}
    e2e_partial_by = {s.departure: s for s in e2e_partial}
    e4w_by = {s.departure: s for s in e4w}
    e4e_by = {s.departure: s for s in e4e}
    e4ww_by = {s.departure: s for s in e4ww}
    e4we_by = {s.departure: s for s in e4we}
    e4su_by = {s.departure: s for s in e4su}
    e2snw_by = {s.departure: s for s in e2snw}
    e2sne_by = {s.departure: s for s in e2sne}
    e4snw_by = {s.departure: s for s in e4snw}
    e4sne_by = {s.departure: s for s in e4sne}
    e3w_by = {s.departure: s for s in e3w}
    e3e_by = {s.departure: s for s in e3e}
    e3ww_by = {s.departure: s for s in e3ww}
    e3we_by = {s.departure: s for s in e3we}
    l3w_by = {s.departure: s for s in l3w}
    l3e_by = {s.departure: s for s in l3e}
    l3ww_by = {s.departure: s for s in l3ww}
    l3we_by = {s.departure: s for s in l3we}

    checks.append(_complete(e1w_by.get("5:35"), 50, 0, "e1_west_0535_complete"))
    checks.append(_complete(e1e_by.get("5:55"), 50, 0, "e1_east_0555_complete"))
    checks.append(_complete(e1we_by.get("7:35"), 50, 0, "e1_weekend_west_0735_complete"))
    checks.append(_complete(e1ww_by.get("6:52"), 50, 0, "e1_weekend_east_0652_complete"))
    checks.append(_stop_time(e1w_by.get("5:35"), "Altza (Donostia)", "5:37", "e1_west_altza"))
    checks.append(_stop_time(e1w_by.get("5:35"), "Usurbil", "6:04", "e1_west_usurbil"))
    checks.append(_stop_time(e1e_by.get("5:55"), "Usurbil", "8:26", "e1_east_usurbil"))
    checks.append(_stop_time(e1e_by.get("5:55"), "Altza (Donostia)", "8:53", "e1_east_altza"))
    checks.append(_stop_time(e1we_by.get("7:35"), "Añorga (Donostia)", "7:56", "e1_weekend_west_anorga"))
    checks.append(_stop_time(e1ww_by.get("6:52"), "Añorga (Donostia)", "9:34", "e1_weekend_east_anorga"))
    checks.append(_day_offset(e1snw_by.get("25:37"), "Deba", 1, "e1_night_west_deba_offset"))
    checks.append(_day_offset(e1sne_by.get("23:45"), "Matiko-Bilbao", 0, "e1_night_east_matiko_offset"))
    checks.append(_day_offset(e1sne_by.get("23:45"), "Deba", 1, "e1_night_east_deba_offset"))
    checks.append(_day_offset(e2snw_by.get("23:34"), "Hendaia", 0, "e2_night_west_hendaia_offset"))
    checks.append(_day_offset(e2snw_by.get("23:34"), "Lasarte-Oria", 1, "e2_night_west_lasarte_offset"))
    checks.append(_day_offset(e2sne_by.get("23:35"), "Lasarte-Oria", 0, "e2_night_east_lasarte_offset"))
    checks.append(_day_offset(e4snw_by.get("22:12"), "Bermeo", 0, "e4_night_west_bermeo_offset"))
    checks.append(_day_offset(e4sne_by.get("23:34"), "Amorebieta Geralekua", 1, "e4_night_east_amorebieta_offset"))
    checks.append(_check(
        "e4_night_west_2212_destination",
        e4snw_by.get("22:12") is not None and e4snw_by["22:12"].destination == "Bermeo",
        "22:12 should terminate at Bermeo on Saturday night",
    ))
    checks.append(_check(
        "e4_night_east_3125_destination",
        e4sne_by.get("31:25") is not None and e4sne_by["31:25"].destination == "Gernika",
        "31:25 should terminate at Gernika",
    ))
    l3fn_by = {s.departure: s for s in l3fn}
    l3sn_by = {s.departure: s for s in l3sn}
    e3sn_by = {s.departure: s for s in e3sn}
    checks.append(_day_offset(l3fn_by.get("24:00"), "Matiko-Bilbao", 1, "l3_night_west_matiko_offset"))
    checks.append(_day_offset(l3sn_by.get("29:45"), "Kukullaga-Etxebarri", 1, "l3_night_west_kukullaga_offset"))
    checks.append(_day_offset(e3sn_by.get("23:50"), "Lezama", 0, "e3_night_west_lezama_offset"))
    checks.append(_day_offset(e3sn_by.get("23:50"), "Kukullaga-Etxebarri", 1, "e3_night_west_kukullaga_offset"))
    checks.append(_complete(e2w_full_by.get("5:34"), 23, 0, "e2_west_0534_complete"))
    checks.append(_complete(e2w_partial_by.get("5:28"), 11, 0, "e2_west_0528_complete"))
    checks.append(_complete(e2we_by.get("6:34"), 23, 0, "e2_weekend_east_0634_complete"))
    checks.append(_complete(e2ww_by.get("6:35"), 23, 0, "e2_weekend_west_0635_complete"))
    checks.append(_complete(e2e_full_by.get("6:05"), 23, 0, "e2_east_0605_complete"))
    checks.append(_complete(e2e_partial_by.get("6:11"), 11, 0, "e2_east_0611_complete"))
    checks.append(_complete(e4w_by.get("6:18"), 25, 0, "e4_west_0618_complete"))
    checks.append(_complete(e4e_by.get("6:10"), 25, 0, "e4_east_0610_complete"))
    checks.append(_complete(e4ww_by.get("7:47"), 25, 0, "e4_weekend_west_0747_complete"))
    checks.append(_complete(e4we_by.get("8:22"), 25, 0, "e4_weekend_east_0822_complete"))
    checks.append(_complete(e2snw_by.get("23:04"), 23, 0, "e2_night_west_2304_complete"))
    checks.append(_complete(e2sne_by.get("23:05"), 23, 0, "e2_night_east_2305_complete"))
    checks.append(_complete(e4snw_by.get("22:12"), 26, 0, "e4_night_west_2212_complete"))
    checks.append(_complete(e4sne_by.get("23:34"), 26, 0, "e4_night_east_2334_complete"))
    checks.append(_check(
        "e4_weekend_sunday_2212_gernika",
        e4su_by.get("22:12") is not None and e4su_by["22:12"].destination == "Gernika",
        "22:12 Sunday/holiday variant should terminate at Gernika",
    ))
    checks.append(_check(
        "e4_weekend_east_2252_gernika",
        e4we_by.get("22:52") is not None and e4we_by["22:52"].destination == "Gernika",
        "22:52 should terminate at Gernika",
    ))
    checks.append(_check(
        "e4_weekend_west_2245_gernika",
        e4ww_by.get("22:45") is not None and e4ww_by["22:45"].destination == "Gernika",
        "22:45 should terminate at Gernika",
    ))
    checks.append(_complete(e3w_by.get("6:06"), 16, 0, "e3_west_0606_complete"))
    checks.append(_complete(e3e_by.get("6:37"), 16, 0, "e3_east_0637_complete"))
    checks.append(_complete(e3ww_by.get("7:24"), 16, 0, "e3_weekend_west_0724_complete"))
    checks.append(_complete(e3we_by.get("7:37"), 16, 0, "e3_weekend_east_0737_complete"))
    checks.append(_complete(l3w_by.get("5:51"), 7, 0, "l3_west_0551_complete"))
    checks.append(_complete(l3e_by.get("5:55"), 7, 0, "l3_east_0555_complete"))
    checks.append(_complete(l3ww_by.get("6:54"), 7, 0, "l3_weekend_west_0654_complete"))
    checks.append(_complete(l3we_by.get("6:52"), 7, 0, "l3_weekend_east_0652_complete"))

    for departure, expected in {"7:35": "8:56", "11:35": "12:56", "18:35": "19:56", "20:35": "21:56"}.items():
        checks.append(_altzola(e1w_by.get(departure), expected, f"altzola_west_{departure.replace(':', '')}"))
    # The other reverse footnote times belong to deferred partial services.
    for departure, expected in {"5:55": None, "9:55": None, "12:55": None, "19:55": "21:26"}.items():
        checks.append(_altzola(e1e_by.get(departure), expected, f"altzola_east_{departure.replace(':', '')}"))

    gaintxurizketa = None
    if e2w_full_by.get("5:34"):
        gaintxurizketa = next(
            (st.time for st in e2w_full_by["5:34"].stop_times if st.stop_name == "Gaintxurizketa (Lezo)"),
            None,
        )
    checks.append(_check("gaintxurizketa", gaintxurizketa == "5:47", f"expected 5:47, got {gaintxurizketa}"))

    rules_by_id = {rule.rule_id: rule for rule in rules}
    rule_expectations = [
        ("E1-WD-0535-1935-60", 60, 15, "e1_west_frequency"),
        ("E1-WD-0555-1955-60", 60, 15, "e1_east_frequency"),
        ("E1-WE-0735-2035-60", 60, 14, "e1_weekend_west_frequency"),
        ("E1-WE-0652-1952-60", 60, 14, "e1_weekend_east_frequency"),
        ("E2-T1-WD-0534-2134-30", 30, 33, "e2_west_full_frequency"),
        ("E2-T1-WD-0528-2228-7.5", 7.5, 137, "e2_west_partial_frequency"),
        ("E2-T1-WD-0605-2235-30", 30, 34, "e2_east_full_frequency"),
        ("E2-T1-WD-0611-2241-7.5", 7.5, 133, "e2_east_partial_frequency"),
        ("E2-T1-WE-0634-2234-30", 30, 33, "e2_weekend_east_frequency"),
        ("E2-T1-WE-0635-2235-30", 30, 33, "e2_weekend_west_frequency"),
        ("E2-T1-PASAIA-ANORGA-SA-0658-2158-7.5", 7.5, 121, "e2_saturday_west_shuttle_frequency"),
        ("E2-T1-PASAIA-ANORGA-SU-0658-1258-60", 60, 30, "e2_sunday_west_shuttle_hourly"),
        ("E2-T1-PASAIA-ANORGA-SU-1258-2158-7.5", 7.5, 73, "e2_sunday_west_shuttle_frequency"),
        ("E2-T1-ANORGA-PASAIA-SA-0711-2241-7.5", 7.5, 125, "e2_saturday_east_shuttle_frequency"),
        ("E2-T1-ANORGA-PASAIA-SU-0641-0826-15", 15, 8, "e2_sunday_east_shuttle_15"),
        ("E2-T1-ANORGA-PASAIA-SU-0826-1341-60", 60, 30, "e2_sunday_east_shuttle_hourly"),
        ("E2-T1-ANORGA-PASAIA-SU-1411-2241-7.5", 7.5, 69, "e2_sunday_east_shuttle_frequency"),
        ("E4-WD-0618-2048-30", 30, 30, "e4_west_frequency"),
        ("E4-WD-0710-1910-30", 30, 25, "e4_east_frequency"),
        ("E4-WE-0747-2147-60", 60, 15, "e4_weekend_west_frequency"),
        ("E4-WE-0822-2122-60", 60, 14, "e4_weekend_east_frequency"),
        ("E3-L3-WD-0606-2021-15", 15, 58, "e3_west_frequency"),
        ("E3-L3-WD-0637-2022-15", 15, 56, "e3_east_frequency"),
        ("E3-L3-WE-0724-2224-30", 30, 31, "e3_weekend_west_frequency"),
        ("E3-L3-WE-0737-2237-30", 30, 31, "e3_weekend_east_frequency"),
        ("E3-L3-WD-0551-2259-7.5", 7.5, 138, "l3_west_frequency"),
        ("E3-L3-WD-0555-2302-7.5", 7.5, 138, "l3_east_frequency"),
        ("E3-L3-WE-0654-2314-10", 10, 99, "l3_weekend_west_frequency"),
        ("E3-L3-WE-0652-2302-10", 10, 98, "l3_weekend_east_frequency"),
        ("E3-L3-MATIKO-KUKULLAGA-FN-2330-0215-15", 15, 12, "l3_friday_night_west_frequency"),
        ("E3-L3-MATIKO-KUKULLAGA-SN-2345-0545-15", 15, 25, "l3_saturday_night_west_frequency"),
        ("E3-L3-KUKULLAGA-MATIKO-FN-2338-0208-15", 15, 11, "l3_friday_night_east_frequency"),
        ("E3-L3-KUKULLAGA-MATIKO-SN-2338-0553-15", 15, 26, "l3_saturday_night_east_frequency"),
        ("E1-EIBAR-ERMUA-WD-0641-2211-60", 60, 63, "e1_eibar_weekday_west_frequency"),
        ("E1-EIBAR-ERMUA-WE-0800-2211-60", 60, 44, "e1_eibar_weekend_west_frequency"),
        ("E1-ERMUA-EIBAR-WD-0631-2131-60", 60, 61, "e1_eibar_weekday_east_frequency"),
        ("E1-ERMUA-EIBAR-WE-0801-2142-60", 60, 42, "e1_eibar_weekend_east_frequency"),
    ]
    for rule_id, interval, count, name in rule_expectations:
        rule = rules_by_id.get(rule_id)
        ok = rule is not None and rule.interval_minutes == interval and len(rule.expanded_service_ids) == count
        detail = "rule missing" if rule is None else f"interval={rule.interval_minutes}, expanded={len(rule.expanded_service_ids)}"
        checks.append(_check(name, ok, detail))

    stray = []
    for service in services:
        for stop_time in service.stop_times:
            if stop_time.time and not (TIME_RE.match(stop_time.time) or stop_time.time == "?"):
                stray.append(f"{service.service_id}:{stop_time.stop_name}={stop_time.time}")
    checks.append(_check("no_stray_symbols", not stray, "; ".join(stray[:5]) or "none"))

    broken = []
    for service in services:
        times = [
            to_minutes(st.time)
            for st in service.stop_times
            if st.time and TIME_RE.match(st.time)
        ]
        if times != sorted(times):
            broken.append(service.service_id)
    checks.append(_check("monotonic_times", not broken, ", ".join(broken[:5]) or "all increasing"))

    unknown = [
        stop_time.stop_name
        for service in services
        for stop_time in service.stop_times
        if stop_time.stop_name not in STOP_REGISTRY
    ]
    checks.append(_check("known_stops", not unknown, f"{len(unknown)} unknown"))

    missing_membership = []
    for service in services:
        expected = {corridor.sheet for corridor in CORRIDORS if corridor_appears_in(service, corridor)}
        if set(service.appears_in) != expected:
            missing_membership.append(service.service_id)
    checks.append(_check("appears_in", not missing_membership, ", ".join(missing_membership[:5]) or "all present"))
    return checks


def write_report(checks: list[Check], path: str = "output/validation.md") -> None:
    from pathlib import Path

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Validation report", "", "| Check | Status | Detail |", "|---|---|---|"]
    for check in checks:
        lines.append(f"| {check.name} | {check.status} | {check.detail} |")
    passed = sum(check.status == "PASS" for check in checks)
    lines.extend(["", f"**{passed}/{len(checks)} passed.**", ""])
    target.write_text("\n".join(lines))
