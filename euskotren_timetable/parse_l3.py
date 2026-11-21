"""Parse the L3 Matiko-Bilbao <-> Kukullaga-Etxebarri weekday local service.

The L3 tables are 7 columns and run at a 7.5-minute headway. The pattern
alternates 7/8 minutes: [7, 8] eastbound and [8, 7] westbound.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E3L3_STOPS, stop_id

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
L3_STOPS = E3L3_STOPS[9:]
L3_REVERSE_STOPS = list(reversed(L3_STOPS))


@dataclass(frozen=True)
class L3Config:
    stops: list[str]
    origin: str
    end: str
    direction: str
    slug: str
    cycle: list[int]
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str
    calendar: str = "WD"
    fixed_interval: int | None = None


FORWARD = L3Config(
    stops=L3_STOPS,
    origin="Matiko-Bilbao",
    end="Kukullaga-Etxebarri",
    direction="Matiko-Kukullaga",
    slug="MATIKO-KUKULLAGA",
    cycle=[7, 8],
    rows=(50, 400, 640, 960, 7, 100),
    note=(820, 875, 50, 400, 50, 400),
    block="L3 Matiko -> Kukullaga weekday",
)

REVERSE = L3Config(
    stops=L3_REVERSE_STOPS,
    origin="Kukullaga-Etxebarri",
    end="Matiko-Bilbao",
    direction="Kukullaga-Matiko",
    slug="KUKULLAGA-MATIKO",
    cycle=[8, 7],
    rows=(750, 1100, 640, 960, 7, 800),
    note=(855, 895, 750, 1100, 750, 1100),
    block="L3 Kukullaga -> Matiko weekday",
)

WEEKEND_FORWARD = L3Config(
    stops=L3_STOPS,
    origin="Matiko-Bilbao",
    end="Kukullaga-Etxebarri",
    direction="Matiko-Kukullaga",
    slug="MATIKO-KUKULLAGA",
    cycle=[7, 8],
    rows=(400, 700, 680, 940, 7, 420),
    note=(875, 895, 500, 540, 400, 700),
    block="L3 Matiko -> Kukullaga weekend",
    calendar="WE",
    fixed_interval=10,
)

WEEKEND_REVERSE = L3Config(
    stops=L3_REVERSE_STOPS,
    origin="Kukullaga-Etxebarri",
    end="Matiko-Bilbao",
    direction="Kukullaga-Matiko",
    slug="KUKULLAGA-MATIKO",
    cycle=[8, 7],
    rows=(1100, 1400, 680, 940, 7, 1120),
    note=(870, 895, 1210, 1235, 1100, 1400),
    block="L3 Kukullaga -> Matiko weekend",
    calendar="WE",
    fixed_interval=10,
)


def _parse_interval(near: list[tuple[float, str]]) -> float | None:
    for i, (_x, word) in enumerate(near):
        if word == "min" and i > 0 and near[i - 1][1].isdigit():
            minutes = int(near[i - 1][1])
            for j in range(i + 1, min(i + 5, len(near))):
                if near[j][1] == "s" and j > 0 and near[j - 1][1].isdigit():
                    return minutes + int(near[j - 1][1]) / 60
            return minutes
        if word in ("h",) and i > 0 and near[i - 1][1].isdigit():
            return int(near[i - 1][1]) * 60
    return None


def _parse_note(words, config: L3Config) -> tuple[str, str, float]:
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
    raise ValueError("L3 frequency note not found")


def _generate_fixed(start: str, end: str, interval: int) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    while current <= last:
        out.append(from_minutes(current))
        current += interval
    return out


def _generate_cyclic(start: str, end: str, cycle: list[int]) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    index = 0
    while current <= last:
        out.append(from_minutes(current))
        current += cycle[index % len(cycle)]
        index += 1
    return out


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: L3Config,
    frequency_rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    notes = [f"7.5-minute frequency {frequency_rule_id}"] if frequency_rule_id else [
        "Explicit service outside the frequency range"
    ]
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
        pattern=["L3"],
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


def parse_l3_direction(
    pdf: str | Path, source_url: str, config: L3Config
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    if not rows:
        raise ValueError("L3 table rows not found")

    grid = build_grid(next(row for row in rows if len(row) == len(config.stops)), config.stops)
    explicit = {}
    for row in rows:
        values = row_to_dict(row, grid)
        if is_time(values.get(config.origin)):
            explicit[values[config.origin]] = values
    if not explicit:
        raise ValueError("L3 full-line row not found")

    start, end, interval = _parse_note(words, config)
    rule_id = (
        f"E3-L3-{config.calendar}-{start.replace(':', '').zfill(4)}-"
        f"{end.replace(':', '').zfill(4)}-{interval}"
    )
    template = explicit[start]
    if config.fixed_interval:
        generated = _generate_fixed(start, end, config.fixed_interval)
    else:
        generated = _generate_cyclic(start, end, config.cycle)

    services: list[Service] = []
    for departure in generated:
        offset = to_minutes(departure) - to_minutes(start)
        record = {
            stop: add_minutes(template[stop], offset) if is_time(template.get(stop)) else template.get(stop, "")
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
        source_text=f"{start} > {end} MAIZTASUNA 7 min 30 s",
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


def parse_l3_weekday(
    pdf: str | Path, source_url: str = "E3/L3 L3 Matiko-Kukullaga"
) -> tuple[list[Service], FrequencyRule]:
    return parse_l3_direction(pdf, source_url, FORWARD)


def parse_l3_reverse(
    pdf: str | Path, source_url: str = "E3/L3 L3 Kukullaga-Matiko"
) -> tuple[list[Service], FrequencyRule]:
    return parse_l3_direction(pdf, source_url, REVERSE)


def parse_l3_weekend(
    pdf: str | Path, source_url: str = "E3/L3 L3 Matiko-Kukullaga weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_l3_direction(pdf, source_url, WEEKEND_FORWARD)


def parse_l3_weekend_reverse(
    pdf: str | Path, source_url: str = "E3/L3 L3 Kukullaga-Matiko weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_l3_direction(pdf, source_url, WEEKEND_REVERSE)
