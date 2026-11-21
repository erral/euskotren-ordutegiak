"""Generate the static HTML site from the normalized timetable services."""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import __version__
from .corridors import CORRIDORS, assign_membership
from .model import Service
from .parse_e1 import to_minutes
from .service_order import (
    CALENDAR_ORDER,
    DIRECTION_ORDER,
    LINE_ORDER,
    corridor_sort_key,
    master_sort_key,
)
from .stops import STOP_REGISTRY

SITE_DIR = Path("output/html")
TEMPLATE_DIR = Path(__file__).parent / "templates"
ASSET_DIR = Path(__file__).parent / "assets"
WORKBOOK_FILENAME = "euskotren_timetables_winter_2026.xlsx"

LINE_SLUGS = {"E1": "e1", "E2-T1": "e2-t1", "E4": "e4", "E3-L3": "e3-l3"}
DIRECTION_SLUGS = {
    direction: direction.lower()
    for directions in DIRECTION_ORDER.values()
    for direction in directions
}
CALENDAR_META = (
    {
        "id": "WD",
        "slug": "weekday",
        "label_eu": "Astegunak",
        "label_es": "Laborables",
    },
    {
        "id": "SA",
        "slug": "saturday",
        "label_eu": "Larunbatak",
        "label_es": "Sábados",
    },
    {
        "id": "SU",
        "slug": "sunday-holiday",
        "label_eu": "Igandeak eta jaiegunak",
        "label_es": "Domingos y festivos",
    },
    {
        "id": "WE",
        "slug": "weekend",
        "label_eu": "Larunbat, igande eta jaiegunak",
        "label_es": "Sábados, domingos y festivos",
    },
    {
        "id": "FN",
        "slug": "friday-night",
        "label_eu": "Ostiral gaua eta jaiegun bezperak",
        "label_es": "Viernes noche y vísperas de festivo",
    },
    {
        "id": "SN",
        "slug": "saturday-night",
        "label_eu": "Larunbat gaua",
        "label_es": "Sábados noche",
    },
)
CALENDAR_BY_ID = {calendar["id"]: calendar for calendar in CALENDAR_META}
NIGHT_CALENDARS = {"FN", "SN"}


def _meta(manifest: dict | None, generated_at: str | None) -> dict[str, Any]:
    files = (manifest or {}).get("files", [])
    first = files[0] if files else {}
    return {
        "season": first.get("season", "Winter 2026"),
        "valid_from": first.get("valid_from", "2026-11-21"),
        "valid_to": first.get("valid_to"),
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "generator_version": __version__,
        "source_manifest": [
            {
                "label": entry.get("label") or "",
                "url": entry.get("url") or "",
                "sha256": entry.get("sha256") or "",
            }
            for entry in files
        ],
    }


def _calendar_data(calendar_id: str) -> dict[str, Any]:
    return CALENDAR_BY_ID[calendar_id]


def _line_data() -> list[dict[str, Any]]:
    return [
        {
            "code": line,
            "slug": LINE_SLUGS[line],
            "name": line,
            "directions": [
                {"name": direction, "slug": DIRECTION_SLUGS[direction]}
                for direction in DIRECTION_ORDER[line]
            ],
        }
        for line in LINE_ORDER
    ]


def _corridor_data() -> list[dict[str, Any]]:
    return [
        {
            "sheet": corridor.sheet,
            "line": corridor.line,
            "direction": corridor.direction,
            "slug": DIRECTION_SLUGS[corridor.direction],
            "stops": list(corridor.stops),
        }
        for corridor in CORRIDORS
    ]


def _stop_data() -> list[dict[str, Any]]:
    return [
        {"stop_id": stop.stop_id, "name": stop.name, "lines": list(stop.lines)}
        for stop in STOP_REGISTRY.values()
    ]


def _service_data(service: Service) -> dict[str, Any]:
    return {
        "service_id": service.service_id,
        "primary_line": service.primary_line,
        "pattern": list(service.pattern),
        "direction": service.direction,
        "calendar": service.calendar,
        "origin": service.origin,
        "destination": service.destination,
        "departure": service.departure,
        "arrival": service.arrival,
        "appears_in": list(service.appears_in),
        "frequency_rule_ids": list(service.frequency_rule_ids),
        "notes": list(service.notes),
        "stop_times": [
            {
                "stop_name": stop_time.stop_name,
                "time": stop_time.time,
                "disposition": stop_time.disposition,
                "day_offset": stop_time.day_offset,
            }
            for stop_time in service.stop_times
        ],
    }


def _cell(stop_time) -> dict[str, str]:
    if stop_time is None:
        return {"display": "", "klass": "empty"}
    if stop_time.disposition == "stop" and stop_time.time:
        return {"display": stop_time.time, "klass": "time"}
    if stop_time.disposition == "unpublished":
        return {"display": "?", "klass": "unpublished"}
    if stop_time.disposition == "pass":
        return {"display": ">", "klass": "pass"}
    return {"display": "", "klass": "empty"}


def _line_sections(services: list[Service], combos: set[tuple[str, str]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for line in LINE_ORDER:
        directions: list[dict[str, Any]] = []
        for corridor in CORRIDORS:
            if corridor.line != line:
                continue
            calendars = [
                _calendar_data(calendar)
                for calendar in CALENDAR_ORDER
                if (corridor.sheet, calendar) in combos
            ]
            if calendars:
                directions.append(
                    {
                        "name": corridor.direction,
                        "slug": DIRECTION_SLUGS[corridor.direction],
                        "calendars": calendars,
                    }
                )
        if directions:
            sections.append(
                {
                    "code": line,
                    "slug": LINE_SLUGS[line],
                    "name": line,
                    "directions": directions,
                }
            )
    return sections


def _corridor_rows(
    services: list[Service], corridor_sheet: str, own_line: str
) -> list[dict[str, Any]]:
    corridor = next(item for item in CORRIDORS if item.sheet == corridor_sheet)
    rows = []
    for service in sorted(
        (service for service in services if corridor_sheet in service.appears_in),
        key=lambda service: corridor_sort_key(service, own_line),
    ):
        by_name = {stop_time.stop_name: stop_time for stop_time in service.stop_times}
        rows.append(
            {
                "service": service,
                "cells": [_cell(by_name.get(stop)) for stop in corridor.stops],
                "notes": "; ".join(service.notes),
            }
        )
    return rows


def _master_rows(services: list[Service]) -> list[dict[str, Any]]:
    by_sheet = {corridor.sheet: corridor for corridor in CORRIDORS}
    rows = []
    for service in services:
        links = []
        for sheet in service.appears_in:
            corridor = by_sheet.get(sheet)
            if corridor is None:
                continue
            links.append(
                {
                    "label": sheet,
                    "url": (
                        f"line/{LINE_SLUGS[corridor.line]}/"
                        f"{DIRECTION_SLUGS[corridor.direction]}/"
                        f"{_calendar_data(service.calendar)['slug']}.html"
                    ),
                }
            )
        rows.append(
            {
                "service": service,
                "search": (f"{service.service_id} {service.origin} {service.destination}").lower(),
                "line": service.primary_line,
                "calendar": service.calendar,
                "calendar_label": (
                    f"{_calendar_data(service.calendar)['label_eu']} / "
                    f"{_calendar_data(service.calendar)['label_es']}"
                ),
                "origin": service.origin,
                "destination": service.destination,
                "departure_minutes": to_minutes(service.departure),
                "departure": service.departure,
                "arrival": service.arrival,
                "pattern": "; ".join(service.pattern),
                "notes": "; ".join(service.notes),
                "corridors": links,
            }
        )
    return rows


def build_site(
    services: list[Service],
    output_dir: str | Path,
    manifest: dict | None = None,
    workbook_path: str | Path | None = None,
    generated_at: str | None = None,
) -> Path:
    """Render the static site and return its output directory."""
    output = Path(output_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    assign_membership(services)
    ordered_services = sorted(services, key=master_sort_key)
    combos = {
        (sheet, service.calendar) for service in ordered_services for sheet in service.appears_in
    }
    meta = _meta(manifest, generated_at)

    workbook_url = None
    if workbook_path is not None and Path(workbook_path).exists():
        downloads = output / "downloads"
        downloads.mkdir()
        shutil.copyfile(workbook_path, downloads / WORKBOOK_FILENAME)
        workbook_url = f"downloads/{WORKBOOK_FILENAME}"

    assets = output / "assets"
    shutil.copytree(ASSET_DIR, assets)
    (output / ".nojekyll").write_text("", encoding="utf-8")

    context = {"meta": meta, "workbook_url": workbook_url}
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    data_dir = output / "data"
    data_dir.mkdir()
    data = {
        "schema_version": 1,
        "meta": meta,
        "lines": _line_data(),
        "calendars": [dict(calendar, order=index) for index, calendar in enumerate(CALENDAR_META)],
        "stops": _stop_data(),
        "corridors": _corridor_data(),
        "services": [_service_data(service) for service in ordered_services],
    }
    (data_dir / "services.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    index_context = dict(
        context,
        root="",
        line_sections=_line_sections(ordered_services, combos),
        calendars=CALENDAR_META,
        title="Euskotren ordutegiak / Horarios",
    )
    (output / "index.html").write_text(
        environment.get_template("index.html").render(index_context), encoding="utf-8"
    )

    master_rows = _master_rows(ordered_services)
    master_context = dict(
        context,
        root="",
        rows=master_rows,
        line_options=[{"code": line, "label": line} for line in LINE_ORDER],
        calendar_options=CALENDAR_META,
        stop_options=sorted(STOP_REGISTRY),
        title="Zerbitzu guztiak / Todos los servicios",
    )
    (output / "master.html").write_text(
        environment.get_template("master.html").render(master_context), encoding="utf-8"
    )

    template = environment.get_template("corridor.html")
    for corridor in CORRIDORS:
        available_calendars = [
            calendar for calendar in CALENDAR_ORDER if (corridor.sheet, calendar) in combos
        ]
        if not available_calendars:
            continue
        directory = (
            output / "line" / LINE_SLUGS[corridor.line] / DIRECTION_SLUGS[corridor.direction]
        )
        directory.mkdir(parents=True, exist_ok=True)
        for calendar in available_calendars:
            calendar_data = _calendar_data(calendar)
            rows = [
                row
                for row in _corridor_rows(ordered_services, corridor.sheet, corridor.line)
                if row["service"].calendar == calendar
            ]
            calendar_links = [
                dict(_calendar_data(other), current=other == calendar)
                for other in available_calendars
            ]
            page_context = dict(
                context,
                root="../../../",
                corridor=corridor,
                calendar=calendar_data,
                calendar_links=calendar_links,
                stops=list(corridor.stops),
                rows=rows,
                night=calendar in NIGHT_CALENDARS,
                title=(f"{corridor.line} · {corridor.direction} · {calendar_data['label_eu']}"),
            )
            (directory / f"{calendar_data['slug']}.html").write_text(
                template.render(page_context), encoding="utf-8"
            )

    return output


def validate_site(output_dir: str | Path = SITE_DIR) -> list[str]:
    """Check internal links, anchors, JSON and the absence of PDFs."""
    output = Path(output_dir)
    errors: list[str] = []
    if not output.exists():
        return [f"site output does not exist: {output}"]

    pdfs = list(output.rglob("*.pdf"))
    if pdfs:
        errors.append(f"PDF files in site output: {', '.join(str(path) for path in pdfs[:3])}")

    data_file = output / "data" / "services.json"
    if not data_file.exists():
        errors.append("missing data/services.json")
    else:
        try:
            json.loads(data_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid data/services.json: {exc}")

    html_files = list(output.rglob("*.html"))
    ids: dict[Path, set[str]] = {}
    refs: list[tuple[Path, str]] = []
    for file in html_files:
        text = file.read_text(encoding="utf-8")
        file_ids = re.findall(r'\bid="([^"]+)"', text)
        if len(file_ids) != len(set(file_ids)):
            errors.append(f"{file}: duplicate id attributes")
        ids[file.resolve()] = set(file_ids)
        for value in re.findall(r'\b(?:href|src)="([^"]+)"', text):
            refs.append((file.resolve(), value))

    for file, value in refs:
        if value.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue
        if value.startswith("#"):
            if value[1:] not in ids.get(file, set()):
                errors.append(f"{file}: missing anchor {value}")
            continue
        path_part, _, fragment = value.partition("#")
        target = (file.parent / path_part).resolve()
        if not target.exists():
            errors.append(f"{file}: broken link {value}")
            continue
        if fragment and target.suffix == ".html":
            if fragment not in ids.get(target, set()):
                errors.append(f"{file}: missing anchor {value}")

    return errors
