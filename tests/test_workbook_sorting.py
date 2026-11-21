import unittest

from openpyxl import Workbook

from euskotren_timetable.model import Service, StopTime
from euskotren_timetable.parse_e1 import add_minutes
from euskotren_timetable.workbook import _corridor_sheet, _master, _readme


def make_service(
    service_id: str,
    calendar: str,
    line: str,
    direction: str,
    departure: str,
    stops: tuple[str, ...] = ("Pasaia", "Altza (Donostia)"),
) -> Service:
    stop_times = [
        StopTime(
            f"S{index:03d}",
            stop,
            index,
            add_minutes(departure, index - 1),
            "stop",
            "test",
        )
        for index, stop in enumerate(stops, 1)
    ]
    return Service(
        service_id=service_id,
        primary_line=line,
        pattern=["test"],
        direction=direction,
        calendar=calendar,
        valid_from="2026-11-21",
        valid_to=None,
        origin=stops[0],
        destination=stops[-1],
        departure=departure,
        arrival=stop_times[-1].time,
        source_pdf="test",
        frequency_rule_ids=[],
        notes=[],
        appears_in=[],
        stop_times=stop_times,
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

    def test_master_is_flat(self):
        wb = Workbook()
        ws = wb.active
        services = [make_service("WD-E1", "WD", "E1", "Pasaia-Matiko", "5:35")]
        _master(ws, services)
        self.assertEqual(ws.cell(row=1, column=1).value, "Service ID")
        self.assertEqual(ws.cell(row=2, column=1).value, "WD-E1")

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
        rows = [ws.cell(row=row, column=1).value for row in range(9, 11)]
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
        rows2 = [ws2.cell(row=row, column=1).value for row in range(9, 11)]
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
        rows = [ws.cell(row=row, column=1).value for row in range(9, 11)]
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
            for row in range(8, 15)
            if isinstance(ws.cell(row=row, column=1).value, str)
            and "/" in ws.cell(row=row, column=1).value
        ]
        self.assertEqual(
            [header.split(" / ")[0] for header in group_headers],
            ["Astegunak", "Larunbatak", "Larunbat, igande eta jaiegunak"],
        )

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
