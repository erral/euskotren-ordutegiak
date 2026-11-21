"""Render the E1/E2 weekday workbook."""

from datetime import UTC, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import __version__
from .corridors import CORRIDORS, services_for_corridor
from .model import FrequencyRule, Service
from .service_order import CALENDAR_ORDER, corridor_sort_key, master_sort_key
from .source_notes import SOURCE_NOTES
from .stops import E1_STOPS, E2_STOPS, SHARED_TRUNKS, STOP_REGISTRY
from .validate import Check

CALENDAR_LABELS = {
    "WD": "Astegunak / Weekday (Monday-Friday laborable)",
    "SA": "Larunbatak / Saturday",
    "SU": "Igandeak eta jaiegunak / Sunday + holiday",
    "WE": "Larunbat, igande eta jaiegunak / Weekend (Saturday, Sunday + holiday)",
    "FN": "Ostiral gaua eta jaiegun bezperak / Friday night + holiday eve",
    "SN": "Larunbat gaua / Saturday night",
}

BLUE = "1F4E79"
LIGHT_BLUE = "DDEBF7"
GREY = "F2F2F2"
WHITE = "FFFFFF"
RED = "F8CBAD"

THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADER_FONT = Font(bold=True, color=WHITE)
HEADER_FILL = PatternFill("solid", fgColor=BLUE)
SECTION_FILL = PatternFill("solid", fgColor=LIGHT_BLUE)
CONDITIONAL_STOPS = {"Altzola (Elgoibar)", "Gaintxurizketa (Lezo)", "Ola (Sondika)"}


def _title(ws, cell: str, value: str, size: int = 16) -> None:
    ws[cell] = value
    ws[cell].font = Font(bold=True, size=size, color=BLUE)


def _header_row(ws, row: int, values: list[str], start_col: int = 1) -> None:
    for offset, value in enumerate(values):
        cell = ws.cell(row=row, column=start_col + offset, value=value)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = BORDER


def _widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def _readme(ws, manifest: dict | None, workbook_name: str) -> None:
    ws.sheet_view.showGridLines = False
    _title(ws, "A1", "Euskotren — single timetable workbook", 18)
    rows = [
        ("Workbook", workbook_name),
        ("Season", "Winter 2026"),
        ("Validity", "from 2026-11-21; open until superseded"),
        ("Generated", datetime.now(UTC).isoformat()),
        ("Generator", f"euskotren-timetable {__version__}"),
        (
            "Scope",
            "E1, E2-T1, E4 and E3/L3 weekdays, combined weekend services, the E2 Saturday/Sunday Añorga shuttle, E1/E2-T1/E4 Saturday night, E3-L3 Friday/Saturday night, the E1 Pasaia-Zumaia, Zaldibar/Matiko-Traña, Elgoibar-Matiko and Eibar-Ermua partials, the E4 22:12/22:45 Gernika variants, E4 Gernika short-turns and the Amorebieta Geltokia transfer column, both directions. Basque names are canonical; Spanish aliases are intentionally omitted.",
        ),
        ("Source", "Official Euskotren winter-2026 PDFs, https://euskotren.eus/eu/tren/ordutegiak"),
        ("Legend", "Blank = does not stop. ? = time not published. Times are 24-hour."),
        (
            "Cross-line",
            "Master > Appears in lists every corridor sheet a service traverses. A service can appear on both E1 and E2.",
        ),
        (
            "Sort order",
            "Services are ordered by calendar, departure time, line and direction; corridor sheets put their own line first when services share a departure. Night times use the extended clock (24:xx/25:xx).",
        ),
        ("Source notes", "Verbatim side notes from the posters are on the Source notes sheet."),
        ("", ""),
        ("Sheet", "Purpose"),
        ("Stops", "Canonical network stops and notes"),
        ("Calendars", "Named service sets"),
        ("Manifest", "Source PDF provenance"),
        ("Coverage", "Included and pending line/calendar patterns"),
        ("Source notes", "Verbatim side notes printed on the posters"),
        ("Master", "One canonical row per service"),
        (
            "E1 Pasaia-Matiko",
            "E1 westbound corridor, including E2 services on the shared Donostia section",
        ),
        (
            "E1 Matiko-Pasaia",
            "E1 eastbound corridor, including E2 services on the shared Donostia section",
        ),
        (
            "E2-T1 Hendaia-Lasarte",
            "E2 westbound corridor, including E1 services on the shared Donostia section",
        ),
        (
            "E2-T1 Lasarte-Hendaia",
            "E2 eastbound corridor, including E1 services on the shared Donostia section",
        ),
        (
            "E4 Matiko-Bermeo",
            "E4 eastbound corridor, including E1 services on the shared Bilbao core",
        ),
        (
            "E4 Bermeo-Matiko",
            "E4 westbound corridor, including E1 services on the shared Bilbao core",
        ),
        ("E3-L3 Lezama-Kukullaga", "E3 branch, including E1/E4 services on the shared Bilbao core"),
        ("E3-L3 Kukullaga-Lezama", "E3 branch, including E1/E4 services on the shared Bilbao core"),
        ("Frequency rules", "Compressed source rules and expanded services"),
        ("Validation", "Structural checks for this run"),
    ]
    for r, (key, value) in enumerate(rows, 3):
        ws.cell(row=r, column=1, value=key).font = Font(bold=True)
        ws.cell(row=r, column=2, value=value).alignment = Alignment(wrap_text=True, vertical="top")
    _widths(ws, {"A": 20, "B": 110})
    if manifest and manifest.get("files"):
        row = len(rows) + 4
        ws.cell(row=row, column=1, value="Manifest files").font = Font(bold=True)
        ws.cell(row=row, column=2, value="; ".join(entry["url"] for entry in manifest["files"]))


def _coverage(ws) -> None:
    headers = ["Line", "Calendar", "Pattern", "Status", "Notes"]
    _header_row(ws, 1, headers)
    rows = [
        (
            "E1",
            "WD",
            "Pasaia-Matiko / Matiko-Pasaia",
            "Included",
            "Weekday through service, Topo times and Pasaia-Zumaia short-turns.",
        ),
        (
            "E1",
            "WE",
            "Full-line both directions",
            "Included",
            "Weekend through service, Topo times and Pasaia-Zumaia short-turns.",
        ),
        (
            "E1",
            "WD",
            "Zaldibar-Matiko / Matiko-Traña refuerzos",
            "Included",
            "Explicit-only weekday reinforcement services.",
        ),
        (
            "E1",
            "WD",
            "Elgoibar-Matiko partial",
            "Included",
            "Elgoibar-origin 30-minute/hourly partials.",
        ),
        ("E1", "WE", "Elgoibar-Matiko partial", "Included", "Weekend hourly partials."),
        ("E1", "WD", "Eibar-Ermua partial", "Included", "Hourly-repeat sequence, weekdays."),
        ("E1", "WE", "Eibar-Ermua partial", "Included", "Hourly-repeat sequence, weekend."),
        (
            "E1",
            "SN",
            "Saturday night",
            "Included",
            "Deba-Matiko / Matiko-Deba night blocks; after-midnight times use 24:xx/25:xx.",
        ),
        ("E2-T1", "WD", "Full-line + Pasaia/Añorga shuttle", "Included", "Both directions."),
        ("E2-T1", "WE", "Full-line both directions", "Included", "30-minute weekend pattern."),
        (
            "E2-T1",
            "SA",
            "Añorga shuttle",
            "Included",
            "Saturday 7.5-minute pattern with explicit early/late services.",
        ),
        (
            "E2-T1",
            "SU",
            "Añorga shuttle",
            "Included",
            "Sunday/holiday 15-minute morning, hourly midday, 7.5-minute afternoon/evening.",
        ),
        (
            "E2-T1",
            "SN",
            "Saturday night",
            "Included",
            "Hendaia-Lasarte / Lasarte-Hendaia full-line night services.",
        ),
        ("E4", "WD", "Full-line both directions", "Included", "Includes the Gernika short-turns."),
        (
            "E4",
            "WE",
            "Full-line main pattern",
            "Included",
            "Includes the 22:52/22:45 Gernika short-turns and weekend Gernika short-turns.",
        ),
        (
            "E4",
            "SU",
            "22:12 Gernika variant",
            "Included",
            "Sunday/holiday-only destination of the 22:12 train.",
        ),
        (
            "E4",
            "SN",
            "Saturday night",
            "Included",
            "Includes the 22:12 Saturday Bermeo special and the Amorebieta Geltokia transfer column.",
        ),
        ("E3-L3", "WD", "E3 Lezama branch + L3 local", "Included", "Both directions."),
        ("E3-L3", "WE", "E3 + L3", "Included", "E3 30 min, L3 10 min."),
        (
            "E3-L3",
            "FN",
            "Friday night / holiday eve",
            "Included",
            "L3 local both directions; 15-minute night pattern.",
        ),
        (
            "E3-L3",
            "SN",
            "Saturday night",
            "Included",
            "L3 local plus E3 Lezama branch Saturday night, both directions.",
        ),
    ]
    for r, values in enumerate(rows, 2):
        for c, value in enumerate(values, 1):
            ws.cell(row=r, column=c, value=value)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{len(rows) + 1}"
    _widths(ws, {"A": 12, "B": 12, "C": 38, "D": 12, "E": 65})


def _stops(ws) -> None:
    _header_row(ws, 1, ["Stop ID", "Name", "Lines", "Notes"])
    notes = {
        "Altzola (Elgoibar)": "Conditional stop: 8:56, 12:56, 19:56, 21:56.",
        "Gaintxurizketa (Lezo)": "Conditional stop, every 30 minutes.",
        "Ola (Sondika)": "Conditional stop; confirm in the calling pattern.",
        "Amorebieta Geltokia": "E1 Bilbao-Donostia stop.",
        "Amorebieta Geralekua": "E4 Bilbao-Bermeo stop; distinct from Geltokia.",
        "Amara Donostia": "Canonical merge of the E1 and E2 Amara labels.",
        "Traña Abadiño": "One stop, not Traña + Abadiño.",
        "Altza (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Herrera (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Intxaurrondo (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Loiola (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Lugaritz (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Añorga (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Errekalde (Donostia)": "Omitted from the E1 42-column table; every train serves it (source side note).",
        "Usurbil": "Omitted from the E1 42-column table; every train serves it (source side note).",
    }
    for row, stop in enumerate(STOP_REGISTRY.values(), 2):
        ws.cell(row=row, column=1, value=stop.stop_id)
        ws.cell(row=row, column=2, value=stop.name)
        ws.cell(row=row, column=3, value=", ".join(stop.lines))
        ws.cell(row=row, column=4, value=notes.get(stop.name, ""))
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:D{len(STOP_REGISTRY) + 1}"
    _widths(ws, {"A": 10, "B": 38, "C": 18, "D": 60})


def _calendars(ws) -> None:
    _header_row(ws, 1, ["Calendar ID", "Name", "Day types", "Valid from", "Valid to", "Notes"])
    rows = [
        ("WD", "Weekday", "Monday-Friday laborable", "2026-11-21", None, "Source weekday block."),
        ("SA", "Saturday", "Saturday", "2026-11-21", None, "Only where the source separates it."),
        (
            "SU",
            "Sunday + holiday",
            "Sunday, holiday",
            "2026-11-21",
            None,
            "Holiday dates deferred.",
        ),
        (
            "WE",
            "Saturday + Sunday + holiday",
            "Saturday, Sunday, holiday",
            "2026-11-21",
            None,
            "Preserve the source grouping.",
        ),
        (
            "FN",
            "Friday night / holiday eve",
            "Friday night, holiday eve",
            "2026-11-21",
            None,
            "Night services; day offset.",
        ),
        (
            "SN",
            "Saturday night",
            "Saturday night",
            "2026-11-21",
            None,
            "Night services; day offset.",
        ),
    ]
    for r, values in enumerate(rows, 2):
        for c, value in enumerate(values, 1):
            ws.cell(row=r, column=c, value=value)
    ws.freeze_panes = "A2"
    _widths(ws, {"A": 12, "B": 28, "C": 30, "D": 12, "E": 12, "F": 45})


def _manifest(ws, manifest: dict | None) -> None:
    headers = [
        "Label",
        "URL",
        "Path",
        "SHA-256",
        "Fetched at",
        "Pages",
        "Season",
        "Valid from",
        "Valid to",
        "Generator version",
    ]
    _header_row(ws, 1, headers)
    if manifest:
        for r, entry in enumerate(manifest.get("files", []), 2):
            values = [
                entry.get("label"),
                entry.get("url"),
                entry.get("path"),
                entry.get("sha256"),
                entry.get("fetched_at"),
                entry.get("page_count"),
                entry.get("season"),
                entry.get("valid_from"),
                entry.get("valid_to"),
                entry.get("generator_version"),
            ]
            for c, value in enumerate(values, 1):
                ws.cell(row=r, column=c, value=value)
    ws.freeze_panes = "A2"
    _widths(
        ws,
        {"A": 26, "B": 60, "C": 35, "D": 68, "E": 26, "F": 8, "G": 14, "H": 12, "I": 12, "J": 16},
    )


def _source_notes(ws) -> None:
    headers = ["Source PDF", "Scope", "Basque note", "Spanish note", "Meaning"]
    _header_row(ws, 1, headers)
    for r, note in enumerate(SOURCE_NOTES, 2):
        for c, key in enumerate(("pdf", "scope", "note_eu", "note_es", "meaning"), 1):
            cell = ws.cell(row=r, column=c, value=note[key])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{len(SOURCE_NOTES) + 1}"
    _widths(ws, {"A": 30, "B": 38, "C": 62, "D": 62, "E": 70})


def _master(ws, services: list[Service]) -> None:
    headers = [
        "Service ID",
        "Primary line",
        "Pattern",
        "Appears in",
        "Direction",
        "Calendar",
        "Valid from",
        "Valid to",
        "Origin",
        "Destination",
        "Departure",
        "Arrival",
        "Source PDF",
        "Frequency rule(s)",
        "Notes",
    ]
    _header_row(ws, 1, headers)
    ordered = sorted(services, key=master_sort_key)
    for r, service in enumerate(ordered, 2):
        values = [
            service.service_id,
            service.primary_line,
            "; ".join(service.pattern),
            "; ".join(service.appears_in),
            service.direction,
            service.calendar,
            service.valid_from,
            service.valid_to,
            service.origin,
            service.destination,
            service.departure,
            service.arrival,
            service.source_pdf,
            "; ".join(service.frequency_rule_ids),
            "; ".join(service.notes),
        ]
        for c, value in enumerate(values, 1):
            cell = ws.cell(row=r, column=c, value=value)
            cell.border = BORDER
            if c == 15:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:O{len(services) + 1}"
    _widths(
        ws,
        {
            "A": 32,
            "B": 12,
            "C": 18,
            "D": 55,
            "E": 18,
            "F": 12,
            "G": 12,
            "H": 12,
            "I": 22,
            "J": 22,
            "K": 10,
            "L": 10,
            "M": 55,
            "N": 30,
            "O": 50,
        },
    )


def _corridor_sheet(
    ws,
    title: str,
    subtitle: str,
    stops: list[str],
    services: list[Service],
    through_stops: set[str],
    own_line: str,
) -> None:
    metadata = [
        "Service ID",
        "Primary line",
        "Pattern",
        "Calendar",
        "Valid from",
        "Valid to",
        "Origin",
        "Destination",
        "Departure",
        "Arrival",
        "Notes",
    ]
    first_stop_col = len(metadata) + 1
    last_col = first_stop_col + len(stops) - 1
    last_letter = get_column_letter(last_col)

    ws.merge_cells(f"A1:{last_letter}1")
    _title(ws, "A1", title, 18)
    ws.merge_cells(f"A2:{last_letter}2")
    ws["A2"] = subtitle
    ws["A2"].font = Font(italic=True, color="595959")
    for offset, value in enumerate(metadata):
        col = 1 + offset
        ws.merge_cells(start_row=4, start_column=col, end_row=7, end_column=col)
        cell = ws.cell(row=4, column=col, value=value)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        cell.border = BORDER

    for index, stop in enumerate(stops):
        col = first_stop_col + index
        if stop in CONDITIONAL_STOPS:
            marker = "conditional"
        elif stop in through_stops:
            marker = "through"
        else:
            marker = "trunk"
        values = [STOP_REGISTRY[stop].stop_id, stop, stop, marker]
        for row_offset, value in enumerate(values):
            cell = ws.cell(row=4 + row_offset, column=col, value=value)
            cell.font = HEADER_FONT if row_offset == 0 else Font(size=9)
            cell.fill = HEADER_FILL if row_offset == 0 else SECTION_FILL
            cell.alignment = Alignment(
                textRotation=90, horizontal="center", vertical="bottom", wrap_text=False
            )
            cell.border = BORDER

    row = 8
    for calendar in CALENDAR_ORDER:
        group = [service for service in services if service.calendar == calendar]
        if not group:
            continue
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=len(metadata))
        header = ws.cell(row=row, column=1, value=CALENDAR_LABELS[calendar])
        header.font = Font(bold=True, color=WHITE)
        header.fill = HEADER_FILL
        header.alignment = Alignment(vertical="center")
        row += 1

        for service in sorted(group, key=lambda item: corridor_sort_key(item, own_line)):
            metadata_values = [
                service.service_id,
                service.primary_line,
                "; ".join(service.pattern),
                service.calendar,
                service.valid_from,
                service.valid_to,
                service.origin,
                service.destination,
                service.departure,
                service.arrival,
                "; ".join(service.notes),
            ]
            for c, value in enumerate(metadata_values, 1):
                cell = ws.cell(row=row, column=c, value=value)
                cell.border = BORDER
                cell.alignment = Alignment(vertical="center", wrap_text=c == 11)
            by_name = {stop_time.stop_name: stop_time for stop_time in service.stop_times}
            for index, stop in enumerate(stops):
                stop_time = by_name.get(stop)
                value = stop_time.time if stop_time and stop_time.time else None
                cell = ws.cell(row=row, column=first_stop_col + index, value=value)
                cell.border = BORDER
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if value == "?":
                    cell.font = Font(bold=True, color="C00000")
            row += 1

    last_service_row = row - 1
    ws.freeze_panes = ws.cell(row=8, column=first_stop_col)
    _widths(
        ws,
        {
            "A": 32,
            "B": 10,
            "C": 18,
            "D": 12,
            "E": 12,
            "F": 12,
            "G": 22,
            "H": 22,
            "I": 10,
            "J": 10,
            "K": 50,
        },
    )
    for index in range(len(stops)):
        ws.column_dimensions[get_column_letter(first_stop_col + index)].width = 5
    for row_index in range(4, 8):
        ws.row_dimensions[row_index].height = 150
    ws.row_dimensions[1].height = 24
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:7"
    ws.print_area = f"A1:{last_letter}{last_service_row}"

    note_row = last_service_row + 2
    ws.cell(
        row=note_row,
        column=1,
        value="Legend: blank = does not stop; ? = time not published; times are 24-hour.",
    )
    ws.cell(row=note_row, column=1).font = Font(italic=True, color="595959")


def _frequency_rules(ws, rules: list[FrequencyRule]) -> None:
    headers = [
        "Rule ID",
        "Source text",
        "Source PDF",
        "Page",
        "Block",
        "Origin",
        "Start",
        "End",
        "Interval (min)",
        "Calendar",
        "Expanded service IDs",
        "Notes",
    ]
    _header_row(ws, 1, headers)
    for r, rule in enumerate(rules, 2):
        values = [
            rule.rule_id,
            rule.source_text,
            rule.source_pdf,
            rule.page,
            rule.block,
            rule.origin,
            rule.start,
            rule.end,
            rule.interval_minutes,
            rule.calendar,
            "; ".join(rule.expanded_service_ids),
            "; ".join(rule.notes),
        ]
        for c, value in enumerate(values, 1):
            cell = ws.cell(row=r, column=c, value=value)
            if c == 11:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    _widths(
        ws,
        {
            "A": 32,
            "B": 55,
            "C": 60,
            "D": 8,
            "E": 38,
            "F": 12,
            "G": 8,
            "H": 8,
            "I": 12,
            "J": 12,
            "K": 100,
            "L": 30,
        },
    )


def _validation(ws, checks: list[Check]) -> None:
    _header_row(ws, 1, ["Check", "Status", "Detail"])
    for r, check in enumerate(checks, 2):
        ws.cell(row=r, column=1, value=check.name)
        status = ws.cell(row=r, column=2, value=check.status)
        if check.status != "PASS":
            status.fill = PatternFill("solid", fgColor=RED)
        ws.cell(row=r, column=3, value=check.detail)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:C{len(checks) + 1}"
    _widths(ws, {"A": 30, "B": 10, "C": 90})


def build_workbook(
    path: str | Path,
    services: list[Service],
    rules: list[FrequencyRule],
    checks: list[Check],
    manifest: dict | None,
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)

    through_stops = set(SHARED_TRUNKS["E1-E2"])
    _readme(wb.create_sheet("README"), manifest, target.name)
    _stops(wb.create_sheet("Stops"))
    _calendars(wb.create_sheet("Calendars"))
    _manifest(wb.create_sheet("Manifest"), manifest)
    _coverage(wb.create_sheet("Coverage"))
    _source_notes(wb.create_sheet("Source notes"))
    _master(wb.create_sheet("Master"), services)
    _corridor_sheet(
        wb.create_sheet("E1 Pasaia-Matiko"),
        "E1 · Pasaia → Matiko-Bilbao",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E1 Pasaia - Matiko_4.pdf",
        E1_STOPS,
        services_for_corridor(services, CORRIDORS[0]),
        through_stops,
        CORRIDORS[0].line,
    )
    _corridor_sheet(
        wb.create_sheet("E1 Matiko-Pasaia"),
        "E1 · Matiko-Bilbao → Pasaia",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E1 Matiko - Pasaia_4.pdf",
        list(CORRIDORS[1].stops),
        services_for_corridor(services, CORRIDORS[1]),
        through_stops,
        CORRIDORS[1].line,
    )
    _corridor_sheet(
        wb.create_sheet("E2-T1 Hendaia-Lasarte"),
        "E2-T1 · Hendaia → Lasarte-Oria",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: T1 Hendaia - Lasarte/Oria",
        E2_STOPS,
        services_for_corridor(services, CORRIDORS[2]),
        through_stops,
        CORRIDORS[2].line,
    )
    _corridor_sheet(
        wb.create_sheet("E2-T1 Lasarte-Hendaia"),
        "E2-T1 · Lasarte-Oria → Hendaia",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: T1 Lasarte/Oria - Hendaia",
        list(CORRIDORS[3].stops),
        services_for_corridor(services, CORRIDORS[3]),
        through_stops,
        CORRIDORS[3].line,
    )
    _corridor_sheet(
        wb.create_sheet("E4 Matiko-Bermeo"),
        "E4 · Matiko-Bilbao → Bermeo",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E4 Bilbao-Bermeo",
        list(CORRIDORS[4].stops),
        services_for_corridor(services, CORRIDORS[4]),
        through_stops,
        CORRIDORS[4].line,
    )
    _corridor_sheet(
        wb.create_sheet("E4 Bermeo-Matiko"),
        "E4 · Bermeo → Matiko-Bilbao",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E4 Bilbao-Bermeo",
        list(CORRIDORS[5].stops),
        services_for_corridor(services, CORRIDORS[5]),
        through_stops,
        CORRIDORS[5].line,
    )
    _corridor_sheet(
        wb.create_sheet("E3-L3 Lezama-Kukullaga"),
        "E3-L3 · Lezama → Kukullaga-Etxebarri",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E3-L3 Lezama / Kukullaga-Etxebarri",
        list(CORRIDORS[6].stops),
        services_for_corridor(services, CORRIDORS[6]),
        through_stops,
        CORRIDORS[6].line,
    )
    _corridor_sheet(
        wb.create_sheet("E3-L3 Kukullaga-Lezama"),
        "E3-L3 · Kukullaga-Etxebarri → Lezama",
        "Winter 2026 · Weekday + weekend · valid from 2026-11-21 · source: E3-L3 Kukullaga-Etxebarri / Lezama",
        list(CORRIDORS[7].stops),
        services_for_corridor(services, CORRIDORS[7]),
        through_stops,
        CORRIDORS[7].line,
    )
    _frequency_rules(wb.create_sheet("Frequency rules"), rules)
    _validation(wb.create_sheet("Validation"), checks)

    wb.save(target)
    return target
