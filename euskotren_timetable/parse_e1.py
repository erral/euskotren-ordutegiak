"""Parse the current E1 Pasaia -> Matiko weekday timetable.

The full-line table omits stops where every train stops. The Pasaia -> Zumaia
partial table supplies those Topo times for the 05:35 service. The weekday
frequency note then expands the hourly pattern across 05:35-19:35, and the
Altzola footnote fills the conditional stop times.
"""

import re
import subprocess
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, E1_STOPS, E1_TOP0_MISSING, stop_id

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
ALTZOLA = "Altzola (Elgoibar)"
MENDARO = "Mendaro"
TOLETXEGAIN = "Toletxegain (Elgoibar)"
MATIKO = "Matiko-Bilbao"


def is_time(value: str | None) -> bool:
    return bool(value and TIME_RE.match(value))


def to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def from_minutes(value: int) -> str:
    value %= 24 * 60
    return f"{value // 60}:{value % 60:02d}"


def add_minutes(value: str, delta: int) -> str:
    return from_minutes(to_minutes(value) + delta)


def parse_altzola_footnote(pdf: str | Path) -> list[str]:
    """Read the Altzola footnote times from the PDF text layer."""
    text = subprocess.run(
        ["pdftotext", "-layout", "-f", "1", "-l", "1", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    text = re.sub(r"\s+", " ", text)
    match = re.search(r"ALTZOLAN(.{0,400})", text, re.IGNORECASE)
    if not match:
        return []
    times: list[str] = []
    for value in re.findall(r"\d{1,2}:\d{2}", match.group(1)):
        if value not in times:
            times.append(value)
    return times


def parse_frequency_note(words: list[tuple[float, float, str]]) -> tuple[str, str, int]:
    """Read the full-line weekday frequency note: start, end, interval minutes."""
    for x, y, word in words:
        if word == "MAIZTASUNA" and 470 <= y <= 510 and 680 <= x <= 700:
            near = [(x2, w2) for x2, y2, w2 in words if abs(y2 - y) <= 12 and 600 <= x2 <= 870]
            near.sort()
            times = [w2 for _x2, w2 in near if TIME_RE.match(w2)]
            interval = None
            for i, (_x2, w2) in enumerate(near):
                compact = re.fullmatch(r"(\d+)(h|min)", w2)
                if compact:
                    interval = int(compact.group(1)) * (60 if compact.group(2) == "h" else 1)
                    break
                if w2 in ("h", "min") and i > 0 and near[i - 1][1].isdigit():
                    interval = int(near[i - 1][1]) * (60 if w2 == "h" else 1)
                    break
            if len(times) >= 2 and interval:
                return times[0], times[1], interval
    raise ValueError("weekday frequency note not found")


def merge_template(full: dict[str, str], partial: dict[str, str]) -> dict[str, str]:
    template: dict[str, str] = {}
    for stop in E1_STOPS:
        if stop in full:
            template[stop] = full[stop]
        elif stop in partial:
            template[stop] = partial[stop]
        else:
            template[stop] = "?"
    return template


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    frequency_rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in E1_STOPS if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    pattern = ["through"] if destination == MATIKO else ["short-turn"]
    notes: list[str] = []
    if frequency_rule_id:
        notes.append(f"Hourly frequency {frequency_rule_id}")
    if destination != MATIKO:
        notes.append(f"Short-turn to {destination}")
    if is_time(record.get(ALTZOLA)):
        notes.append("Altzola conditional stop")

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(E1_STOPS, 1):
        value = record.get(stop, "")
        if is_time(value):
            disposition, time = "stop", from_minutes(to_minutes(value))
        elif value == ">":
            disposition, time = "pass", None
        elif value == "-":
            disposition, time = "not_served", None
        elif value == "?":
            disposition, time = "unpublished", "?"
        else:
            disposition, time = "not_served", None
        stop_times.append(
            StopTime(stop_id(stop), stop, sequence, time, disposition, source.get(stop, ""))
        )

    return Service(
        service_id=f"E1-PASAIA-MATIKO-WD-{departure.replace(':', '').zfill(4)}",
        primary_line="E1",
        pattern=pattern,
        direction="Pasaia-Matiko",
        calendar="WD",
        valid_from="2026-11-21",
        valid_to=None,
        origin=origin,
        destination=destination,
        departure=from_minutes(to_minutes(origin_time)),
        arrival=from_minutes(to_minutes(arrival)),
        source_pdf=source_url,
        frequency_rule_ids=[frequency_rule_id] if frequency_rule_id else [],
        notes=notes,
        appears_in=["E1 Pasaia-Matiko", "E2-T1 Hendaia-Lasarte"],
        stop_times=stop_times,
    )


def parse_e1_weekday(
    pdf: str | Path, source_url: str = "E1 Pasaia - Matiko_4.pdf"
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)

    from .parse_e1_partial import (
        FORWARD_WEEKDAY,
        expand_partial_block,
        fill_service_from_partial,
    )

    full_rows = cluster_rows(words, 40, 1420, 430, 570, 20, 110)
    partial_services = expand_partial_block(words, FORWARD_WEEKDAY)
    if not full_rows or not partial_services:
        raise ValueError(
            f"could not find E1 tables: full={len(full_rows)} partial={len(partial_services)}"
        )

    full_grid = build_grid(full_rows[0], E1_FULL_42)

    full_services = [
        (row_to_dict(row, full_grid).get("Pasaia", "?"), row_to_dict(row, full_grid))
        for row in full_rows
    ]

    template_departure, template_full = full_services[0]
    template = merge_template(template_full, partial_services.get(template_departure, {}))

    start, end, interval = parse_frequency_note(words)
    footnote_times = parse_altzola_footnote(pdf)
    rule_id = f"E1-WD-{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-{interval}"

    explicit = {departure: values for departure, values in full_services}
    departures: list[str] = []
    current = to_minutes(start)
    while current <= to_minutes(end):
        departures.append(from_minutes(current))
        current += interval

    services: list[Service] = []
    for departure in departures:
        offset = to_minutes(departure) - to_minutes(start)
        record: dict[str, str] = {}
        source: dict[str, str] = {}
        for stop in E1_STOPS:
            value = template[stop]
            if is_time(value):
                record[stop] = add_minutes(value, offset)
            else:
                record[stop] = value
            source[stop] = "frequency"

        if departure in explicit:
            for stop, value in explicit[departure].items():
                record[stop] = value
                source[stop] = "full"

        services.append(_build_service(departure, record, source, source_url, rule_id))

    # The 20:35 service is outside the hourly rule and is a short-turn.
    if "20:35" in explicit:
        record = {}
        source = {}
        for stop in E1_STOPS:
            if stop in explicit["20:35"]:
                record[stop] = explicit["20:35"][stop]
                source[stop] = "full"
            elif stop in E1_TOP0_MISSING:
                record[stop] = "?"
                source[stop] = "unpublished"
            else:
                record[stop] = ""
                source[stop] = "not_served"
        services.append(_build_service("20:35", record, source, source_url, None))

    # Altzola footnote: fill conditional stops where the adjacent times bracket it.
    for service in services:
        altzola = next(st for st in service.stop_times if st.stop_name == ALTZOLA)
        if altzola.disposition != "pass":
            continue
        mendaro = next(st for st in service.stop_times if st.stop_name == MENDARO)
        toletxegain = next(st for st in service.stop_times if st.stop_name == TOLETXEGAIN)
        if not (is_time(mendaro.time) and is_time(toletxegain.time)):
            continue
        for value in footnote_times:
            if to_minutes(mendaro.time) < to_minutes(value) < to_minutes(toletxegain.time):
                altzola.time = value
                altzola.disposition = "stop"
                altzola.source = "footnote"
                if "Altzola conditional stop" not in service.notes:
                    service.notes.append("Altzola conditional stop")
                break

    for service in services:
        fill_service_from_partial(
            service,
            partial_services,
            "Pasaia",
            E1_TOP0_MISSING,
            "Topo times from Pasaia-Zumaia partial table",
        )

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=f"{start} > {end} MAIZTASUNA FRECUENCIA {interval // 60} h",
        source_pdf=source_url,
        page=1,
        block="E1 Pasaia -> Matiko weekday",
        origin="Pasaia",
        start=start,
        end=end,
        interval_minutes=interval,
        calendar="WD",
        expanded_service_ids=[
            service.service_id for service in services if service.frequency_rule_ids
        ],
    )
    return services, rule
