import unittest

from openpyxl import Workbook

from euskotren_timetable.service_order import corridor_sort_key, master_sort_key
from euskotren_timetable.workbook import (
    CALENDAR_LABELS,
    _corridor_sheet,
    _master,
    _readme,
)
from tests.support import make_service as _make_service

LINE_CODES = {"E1", "E2-T1", "E4", "E3-L3"}


def service_rows(ws) -> list[int]:
    return [
        row
        for row in range(1, ws.max_row + 1)
        if ws.cell(row=row, column=2).value in LINE_CODES
    ]


def make_service(
    service_id: str,
    calendar: str,
    line: str,
    direction: str,
    departure: str,
    stops: tuple[str, ...] = ("Pasaia", "Altza (Donostia)"),
):
    return _make_service(
        service_id, calendar, line, direction, departure, stops=stops
    )


class WorkbookSortingTests(unittest.TestCase):
    def test_master_uses_calendar_first_order(self):
        wb = Workbook()
        ws = wb.active
        services = [
            make_service("WE-E1", "WE", "E1", "Pasaia-Matiko", "8:00"),
            make_service("WD-E2", "WD", "E2-T1", "Hendaia-Lasarte", "5:35"),
            make_service("WD-E1", "WD", "E1", "Pasaia-Matiko", "5:35"),
        ]
        _master(ws, services)
        rows = [ws.cell(row=row, column=1).value for row in range(2, 5)]
        self.assertEqual(rows, ["WD-E1", "WD-E2", "WE-E1"])

    def test_master_has_no_section_headers(self):
        wb = Workbook()
        ws = wb.active
        services = [
            make_service("WD-E1", "WD", "E1", "Pasaia-Matiko", "5:35"),
            make_service("WE-E1", "WE", "E1", "Pasaia-Matiko", "8:00"),
        ]
        _master(ws, services)
        self.assertEqual(ws.cell(row=1, column=1).value, "Service ID")
        ids = [ws.cell(row=row, column=1).value for row in range(2, 4)]
        self.assertEqual(ids, ["WD-E1", "WE-E1"])
        self.assertTrue(all(isinstance(value, str) and "-" in value for value in ids))

    def test_corridor_own_line_first_at_equal_departure(self):
        services = [
            make_service("E2-SERVICE", "WD", "E2-T1", "Hendaia-Lasarte", "5:35"),
            make_service("E1-SERVICE", "WD", "E1", "Pasaia-Matiko", "5:35"),
        ]
        wb = Workbook()
        ws = wb.active
        _corridor_sheet(
            ws,
            "E1 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            services,
            set(),
            "E1",
        )
        rows = [ws.cell(row=row, column=1).value for row in service_rows(ws)]
        self.assertEqual(rows, ["E1-SERVICE", "E2-SERVICE"])

        wb2 = Workbook()
        ws2 = wb2.active
        _corridor_sheet(
            ws2,
            "E2 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            services,
            set(),
            "E2-T1",
        )
        rows2 = [ws2.cell(row=row, column=1).value for row in service_rows(ws2)]
        self.assertEqual(rows2, ["E2-SERVICE", "E1-SERVICE"])

    def test_corridor_departure_beats_own_line(self):
        services = [
            make_service("E1-LATER", "WD", "E1", "Pasaia-Matiko", "5:35"),
            make_service("E2-EARLY", "WD", "E2-T1", "Hendaia-Lasarte", "5:28"),
        ]
        wb = Workbook()
        ws = wb.active
        _corridor_sheet(
            ws,
            "E1 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            services,
            set(),
            "E1",
        )
        rows = [ws.cell(row=row, column=1).value for row in service_rows(ws)]
        self.assertEqual(rows, ["E2-EARLY", "E1-LATER"])

    def test_corridor_calendar_blocks_in_order(self):
        services = [
            make_service("WE-SERVICE", "WE", "E1", "Pasaia-Matiko", "8:00"),
            make_service("SA-SERVICE", "SA", "E1", "Pasaia-Matiko", "8:00"),
            make_service("WD-SERVICE", "WD", "E1", "Pasaia-Matiko", "8:00"),
        ]
        wb = Workbook()
        ws = wb.active
        _corridor_sheet(
            ws,
            "E1 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            services,
            set(),
            "E1",
        )
        group_headers = [
            ws.cell(row=row, column=1).value
            for row in range(1, ws.max_row + 1)
            if ws.cell(row=row, column=1).value in CALENDAR_LABELS.values()
        ]
        self.assertEqual(group_headers, [
            CALENDAR_LABELS["WD"],
            CALENDAR_LABELS["SA"],
            CALENDAR_LABELS["WE"],
        ])

    def test_corridor_has_no_autofilter(self):
        wb = Workbook()
        ws = wb.active
        _corridor_sheet(
            ws,
            "E1 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            [make_service("WD-E1", "WD", "E1", "Pasaia-Matiko", "5:35")],
            set(),
            "E1",
        )
        self.assertIsNone(ws.auto_filter.ref)

    def test_master_keeps_autofilter(self):
        wb = Workbook()
        ws = wb.active
        services = [make_service("WD-E1", "WD", "E1", "Pasaia-Matiko", "5:35")]
        _master(ws, services)
        self.assertEqual(ws.auto_filter.ref, "A1:O2")

    def test_rendered_rows_are_monotonic(self):
        services = [
            make_service("E2-A", "WD", "E2-T1", "Hendaia-Lasarte", "5:28"),
            make_service("E1-B", "WD", "E1", "Pasaia-Matiko", "5:35"),
            make_service("E2-C", "WD", "E2-T1", "Hendaia-Lasarte", "5:35"),
            make_service("WE-D", "WE", "E1", "Pasaia-Matiko", "8:00"),
        ]
        by_id = {service.service_id: service for service in services}

        master_wb = Workbook()
        master_ws = master_wb.active
        _master(master_ws, services)
        master_ids = [
            master_ws.cell(row=row, column=1).value
            for row in range(2, master_ws.max_row + 1)
        ]
        master_keys = [master_sort_key(by_id[sid]) for sid in master_ids]
        self.assertEqual(master_keys, sorted(master_keys))

        corridor_wb = Workbook()
        corridor_ws = corridor_wb.active
        _corridor_sheet(
            corridor_ws,
            "E1 · test",
            "subtitle",
            ["Pasaia", "Altza (Donostia)"],
            services,
            set(),
            "E1",
        )
        corridor_ids = [
            corridor_ws.cell(row=row, column=1).value
            for row in service_rows(corridor_ws)
        ]
        corridor_keys = [
            corridor_sort_key(by_id[sid], "E1") for sid in corridor_ids
        ]
        self.assertEqual(corridor_keys, sorted(corridor_keys))

    def test_readme_documents_sort_order(self):
        wb = Workbook()
        ws = wb.active
        _readme(ws, None, "test.xlsx")
        values = {
            ws.cell(row=row, column=1).value: ws.cell(row=row, column=2).value
            for row in range(1, ws.max_row + 1)
        }
        self.assertIn("Sort order", values)
        self.assertIn("calendar, departure time, line and direction", values["Sort order"])


if __name__ == "__main__":
    unittest.main()
