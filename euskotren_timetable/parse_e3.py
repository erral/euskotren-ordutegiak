"""Parse the E3 Lezama <-> Kukullaga-Etxebarri weekday tables.

The E3/L3 poster has L3 (Matiko-Kukullaga) and E3 (Lezama-Kukullaga) tables.
This slice parses the E3 pattern only; the L3 local pattern is deferred.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E3L3_STOPS, stop_id

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")


@dataclass(frozen=True)
class E3Config:
    stops: list[str]
    origin: str
    end: str
    direction: str
    slug: str
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str
    calendar: str = "WD"


FORWARD = E3Config(
    stops=E3L3_STOPS,
    origin="Lezama",
    end="Kukullaga-Etxebarri",
    direction="Lezama-Kukullaga",
    slug="LEZAMA-KUKULLAGA",
    rows=(50, 700, 1365, 1620, 16, 100),
    note=(1460, 1485, 50, 700, 50, 700),
    block="E3 Lezama -> Kukullaga-Etxebarri weekday",
)

REVERSE = E3Config(
    stops=list(reversed(E3L3_STOPS)),
    origin="Kukullaga-Etxebarri",
    end="Lezama",
    direction="Kukullaga-Lezama",
    slug="KUKULLAGA-LEZAMA",
    rows=(750, 1400, 1365, 1620, 16, 800),
    note=(1460, 1485, 750, 1400, 750, 1400),
    block="E3 Kukullaga-Etxebarri -> Lezama weekday",
)

WEEKEND_FORWARD = E3Config(
    stops=E3L3_STOPS,
    origin="Lezama",
    end="Kukullaga-Etxebarri",
    direction="Lezama-Kukullaga",
    slug="LEZAMA-KUKULLAGA",
    rows=(50, 700, 1640, 1760, 16, 100),
    note=(1675, 1700, 50, 700, 50, 700),
    block="E3 Lezama -> Kukullaga-Etxebarri weekend",
    calendar="WE",
)

WEEKEND_REVERSE = E3Config(
    stops=list(reversed(E3L3_STOPS)),
    origin="Kukullaga-Etxebarri",
    end="Lezama",
    direction="Kukullaga-Lezama",
    slug="KUKULLAGA-LEZAMA",
    rows=(750, 1400, 1640, 1760, 16, 800),
    note=(1680, 1705, 750, 1400, 750, 1400),
    block="E3 Kukullaga-Etxebarri -> Lezama weekend",
    calendar="WE",
)


def _parse_interval(near: list[tuple[float, str]]) -> int | None:
    for i, (_x, word) in enumerate(near):
        compact = re.fullmatch(r"(\d+)(h|min)", word)
        if compact:
            return int(compact.group(1)) * (60 if compact.group(2) == "h" else 1)
        if word in ("h", "min") and i > 0 and near[i - 1][1].isdigit():
            return int(near[i - 1][1]) * (60 if word == "h" else 1)
    return None


def _parse_note(words, config: E3Config) -> tuple[str, str, int]:
    y_min, y_max, x_min, x_max, near_x_min, near_x_max = config.note
    for x, y, word in words:
        if word == "MAIZTASUNA" and y_min <= y <= y_max and x_min <= x <= x_max:
            near = [
                (x2, w2)
                for x2, y2, w2 in words
                if abs(y2 - y) <= 12 and near_x_min <= x2 <= near_x_max
            ]
            near.sort()
            times = [w2 for _x2, w2 in near if TIME_RE.match(w2)]
            interval = _parse_interval(near)
            if len(times) >= 2 and interval:
                return times[0], times[1], interval
    raise ValueError("E3 frequency note not found")


def _generate(start: str, end: str, interval: int) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    while current <= last:
        out.append(from_minutes(current))
        current += interval
    return out


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: E3Config,
    frequency_rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    notes = (
        [f"15-minute frequency {frequency_rule_id}"]
        if frequency_rule_id
        else ["Explicit service outside the frequency range"]
    )
    if config.calendar == "WE":
        notes.insert(0, "Weekend (Saturday, Sunday + holiday)")

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(config.stops, 1):
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
        service_id=f"E3-L3-{config.slug}-{config.calendar}-{departure.replace(':', '').zfill(4)}",
        primary_line="E3-L3",
        pattern=["E3"],
        direction=config.direction,
        calendar=config.calendar,
        valid_from="2026-11-21",
        valid_to=None,
        origin=origin,
        destination=destination,
        departure=from_minutes(to_minutes(origin_time)),
        arrival=from_minutes(to_minutes(arrival)),
        source_pdf=source_url,
        frequency_rule_ids=[frequency_rule_id] if frequency_rule_id else [],
        notes=notes,
        appears_in=[],
        stop_times=stop_times,
    )


def parse_e3_direction(
    pdf: str | Path, source_url: str, config: E3Config
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    if not rows:
        raise ValueError("E3 table rows not found")

    grid = build_grid(next(row for row in rows if len(row) == len(config.stops)), config.stops)
    explicit = {}
    for row in rows:
        values = row_to_dict(row, grid)
        if is_time(values.get(config.origin)):
            explicit[values[config.origin]] = values
    if not explicit:
        raise ValueError("E3 full-line row not found")

    start, end, interval = _parse_note(words, config)
    start = from_minutes(to_minutes(start))
    end = from_minutes(to_minutes(end))
    rule_id = (
        f"E3-L3-{config.calendar}-{start.replace(':', '').zfill(4)}-"
        f"{end.replace(':', '').zfill(4)}-{interval}"
    )
    template = explicit[start]
    generated = _generate(start, end, interval)

    services: list[Service] = []
    for departure in generated:
        offset = to_minutes(departure) - to_minutes(start)
        record = {
            stop: add_minutes(template[stop], offset)
            if is_time(template.get(stop))
            else template.get(stop, "")
            for stop in config.stops
        }
        source = {stop: "frequency" for stop in config.stops}
        if departure in explicit:
            for stop, value in explicit[departure].items():
                record[stop] = value
                source[stop] = "full"
        services.append(_build_service(departure, record, source, source_url, config, rule_id))

    for departure, values in explicit.items():
        if departure in generated:
            continue
        record = {stop: values.get(stop, "") for stop in config.stops}
        source = {stop: ("full" if stop in values else "not_served") for stop in config.stops}
        services.append(_build_service(departure, record, source, source_url, config, None))

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=f"{start} > {end} MAIZTASUNA {interval} min",
        source_pdf=source_url,
        page=1,
        block=config.block,
        origin=config.origin,
        start=start,
        end=end,
        interval_minutes=interval,
        calendar=config.calendar,
        expanded_service_ids=[
            service.service_id for service in services if rule_id in service.frequency_rule_ids
        ],
    )
    return services, rule


def parse_e3_weekday(
    pdf: str | Path, source_url: str = "E3/L3 Lezama-Kukullaga"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e3_direction(pdf, source_url, FORWARD)


def parse_e3_reverse(
    pdf: str | Path, source_url: str = "E3/L3 Kukullaga-Lezama"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e3_direction(pdf, source_url, REVERSE)


def parse_e3_weekend(
    pdf: str | Path, source_url: str = "E3/L3 Lezama-Kukullaga weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e3_direction(pdf, source_url, WEEKEND_FORWARD)


def parse_e3_weekend_reverse(
    pdf: str | Path, source_url: str = "E3/L3 Kukullaga-Lezama weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e3_direction(pdf, source_url, WEEKEND_REVERSE)
