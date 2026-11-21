import unittest

from euskotren_timetable.validate import validate
from tests.support import make_service


def find_check(checks, name):
    return next(check for check in checks if check.name == name)


class ValidateSortingTests(unittest.TestCase):
    def test_duplicate_service_ids_fail(self):
        services = [
            make_service("SAME", "WD", "E1", "Pasaia-Matiko", "5:35"),
            make_service("SAME", "WD", "E1", "Pasaia-Matiko", "5:35"),
        ]
        checks = validate(services, [])
        self.assertEqual(find_check(checks, "service_ids_unique").status, "FAIL")

    def test_unknown_direction_fails_sort_values(self):
        services = [
            make_service("BAD", "WD", "E1", "Wrong-Direction", "5:35"),
        ]
        checks = validate(services, [])
        self.assertEqual(find_check(checks, "service_sort_values").status, "FAIL")

    def test_missing_departure_fails(self):
        service = make_service("BAD", "WD", "E1", "Pasaia-Matiko", "5:35")
        service.departure = ""
        checks = validate([service], [])
        self.assertEqual(find_check(checks, "service_departures_present").status, "FAIL")
        self.assertEqual(find_check(checks, "service_sort_values").status, "FAIL")


if __name__ == "__main__":
    unittest.main()
