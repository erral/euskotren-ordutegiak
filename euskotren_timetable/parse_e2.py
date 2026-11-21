"""Parse the E2/T1 weekday timetables in both directions.

Each direction has a full-line table and a Pasaia/Añorga shuttle table.
The full-line headway is 30 minutes; the shuttle is 7.5 minutes.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E2_STOPS, stop_id

E2_FULL = E2_STOPS
E2_PARTIAL = E2_STOPS[10:21]
E2_REVERSE_STOPS = list(reversed(E2_STOPS))
E2_REVERSE_PARTIAL = list(reversed(E2_PARTIAL))
TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")


@dataclass(frozen=True)
class DirectionConfig:
    stops: list[str]
    partial_stops: list[str]
    direction: str
    direction_slug: str
    full_origin: str
    full_end: str
    partial_origin: str
    full_rows: tuple[float, float, float, float, int, float]
    partial_rows: tuple[float, float, float, float, int, float]
    full_note: tuple[float, float, float, float, float, float]
    partial_note: tuple[float, float, float, float, float, float]
    shuttle_cycle: list[int]
    full_block: str
    partial_block: str


FORWARD = DirectionConfig(
    stops=E2_FULL,
    partial_stops=E2_PARTIAL,
    direction="Hendaia-Lasarte",
    direction_slug="HENDAIA-LASARTE",
    full_origin="Hendaia",
    full_end="Lasarte-Oria",
    partial_origin="Pasaia",
    full_rows=(50, 850, 700, 850, 20, 120),
    partial_rows=(880, 1400, 690, 890, 8, 920),
    full_note=(740, 780, 400, 420, 300, 600),
    partial_note=(795, 825, 1060, 1090, 950, 1280),
    shuttle_cycle=[7, 8, 8, 7],
    full_block="E2-T1 Hendaia -> Lasarte-Oria weekday",
    partial_block="E2-T1 Pasaia -> Anorga weekday",
)

REVERSE = DirectionConfig(
    stops=E2_REVERSE_STOPS,
    partial_stops=E2_REVERSE_PARTIAL,
    direction="Lasarte-Hendaia",
    direction_slug="LASARTE-HENDAIA",
    full_origin="Lasarte-Oria",
    full_end="Hendaia",
    partial_origin="Añorga (Donostia)",
    full_rows=(50, 900, 700, 800, 20, 120),
    partial_rows=(900, 1400, 715, 910, 8, 940),
    full_note=(736, 756, 385, 405, 300, 600),
    partial_note=(831, 851, 1075, 1095, 950, 1280),
    shuttle_cycle=[8, 7, 8, 7],
    full_block="E2-T1 Lasarte-Oria -> Hendaia weekday",
    partial_block="E2-T1 Anorga -> Pasaia weekday",
)


def _parse_interval(near: list[tuple[float, str]]) -> float | None:
    for i, (_x, word) in enumerate(near):
        lower = word.lower()
        compact = re.fullmatch(r"(\d+(?:[.,]\d+)?)(h|min)", lower)
        if compact:
            number = float(compact.group(1).replace(",", "."))
            return number * (60 if compact.group(2) == "h" else 1)
        if lower in ("h", "min") and i > 0:
            try:
                number = float(near[i - 1][1].replace(",", "."))
            except ValueError:
                continue
            return number * (60 if lower == "h" else 1)
    return None


def parse_frequency_note(
    words: list[tuple[float, float, str]],
    y_min: float,
    y_max: float,
    x_min: float,
    x_max: float,
    near_x_min: float,
    near_x_max: float,
) -> tuple[str, str, float]:
    for x, y, word in words:
        if word in ("MAIZTASUNA", "MAIZATSUNA") and y_min <= y <= y_max and x_min <= x <= x_max:
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
    raise ValueError("frequency note not found in the requested region")


def generate_fixed(start: str, end: str, interval: float) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    step = int(round(interval))
    out = []
    while current <= last:
        out.append(from_minutes(current))
        current += step
    return out


def generate_cyclic(start: str, end: str, cycle: list[int]) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    index = 0
    while current <= last:
        out.append(from_minutes(current))
        current += cycle[index % len(cycle)]
        index += 1
    return out


def _format_interval(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    stops: list[str],
    config: DirectionConfig,
    frequency_rule_id: str | None,
    notes: list[str],
) -> Service:
    timed = [(stop, record[stop]) for stop in stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    is_full = is_time(record.get(config.full_end))
    pattern = ["full"] if is_full else ["short-turn"]

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(stops, 1):
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
        service_id=f"E2-T1-{config.direction_slug}-WD-{departure.replace(':', '').zfill(4)}",
        primary_line="E2-T1",
        pattern=pattern,
        direction=config.direction,
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
        appears_in=[],
        stop_times=stop_times,
    )


def parse_e2_direction(
    pdf: str | Path,
    source_url: str,
    config: DirectionConfig,
) -> tuple[list[Service], list[FrequencyRule]]:
    words = words_from_pdf(pdf, page=1)
    full_rows = cluster_rows(words, *config.full_rows)
    partial_rows = cluster_rows(words, *config.partial_rows)
    if len(full_rows) < 2 or len(partial_rows) < 2:
        raise ValueError(
            f"could not find E2 tables: full={len(full_rows)} partial={len(partial_rows)}"
        )

    full_grid = build_grid(full_rows[0], config.stops)
    partial_grid = build_grid(partial_rows[0], config.partial_stops)
    full = [
        (row_to_dict(row, full_grid).get(config.full_origin, "?"), row_to_dict(row, full_grid))
        for row in full_rows
    ]
    partial = [
        (row_to_dict(row, partial_grid).get(config.partial_origin, "?"), row_to_dict(row, partial_grid))
        for row in partial_rows
    ]
    full_explicit = {departure: values for departure, values in full}
    partial_explicit = {departure: values for departure, values in partial}

    full_start, full_end, full_interval = parse_frequency_note(words, *config.full_note)
    partial_start, partial_end, partial_interval = parse_frequency_note(words, *config.partial_note)

    full_rule_id = (
        f"E2-T1-WD-{full_start.replace(':', '').zfill(4)}-"
        f"{full_end.replace(':', '').zfill(4)}-{_format_interval(full_interval)}"
    )
    partial_rule_id = (
        f"E2-T1-WD-{partial_start.replace(':', '').zfill(4)}-"
        f"{partial_end.replace(':', '').zfill(4)}-{_format_interval(partial_interval)}"
    )

    full_template = full_explicit.get(full_start)
    if full_template is None:
        full_template = next(
            values for departure, values in full if to_minutes(departure) >= to_minutes(full_start)
        )
    partial_template = partial_explicit.get(partial_start)
    if partial_template is None:
        partial_template = next(
            values for departure, values in partial if to_minutes(departure) >= to_minutes(partial_start)
        )

    services: list[Service] = []
    full_departures = generate_fixed(full_start, full_end, full_interval)
    for departure in full_departures:
        offset = to_minutes(departure) - to_minutes(full_start)
        record = {
            stop: add_minutes(full_template[stop], offset)
            if is_time(full_template.get(stop))
            else full_template.get(stop, "")
            for stop in config.stops
        }
        source = {stop: "frequency" for stop in config.stops}
        if departure in full_explicit:
            for stop, value in full_explicit[departure].items():
                record[stop] = value
                source[stop] = "full"
        is_full = is_time(record.get(config.full_end))
        notes = (
            [f"30-minute frequency {full_rule_id}"]
            if is_full
            else [f"Short-turn to {record.get(config.full_end, '?')}"]
        )
        services.append(
            _build_service(
                departure,
                record,
                source,
                source_url,
                config.stops,
                config,
                full_rule_id if is_full else None,
                notes,
            )
        )

    for departure, values in full_explicit.items():
        if departure in full_departures:
            continue
        record = {stop: values.get(stop, "") for stop in config.stops}
        source = {stop: ("full" if stop in values else "not_served") for stop in config.stops}
        notes = ["Explicit service outside the frequency range"]
        if not is_time(record.get(config.full_end)):
            notes.append(f"Short-turn to {record.get(config.full_end, '?')}")
        services.append(
            _build_service(
                departure,
                record,
                source,
                source_url,
                config.stops,
                config,
                None,
                notes,
            )
        )

    partial_departures = generate_cyclic(partial_start, partial_end, config.shuttle_cycle)
    for departure in partial_departures:
        offset = to_minutes(departure) - to_minutes(partial_start)
        record = {
            stop: add_minutes(partial_template[stop], offset)
            if is_time(partial_template.get(stop))
            else partial_template.get(stop, "")
            for stop in config.partial_stops
        }
        source = {stop: "frequency" for stop in config.partial_stops}
        if departure in partial_explicit:
            for stop, value in partial_explicit[departure].items():
                record[stop] = value
                source[stop] = "full"
        services.append(
            _build_service(
                departure,
                record,
                source,
                source_url,
                config.partial_stops,
                config,
                partial_rule_id,
                [f"7.5-minute frequency {partial_rule_id}"],
            )
        )

    for departure, values in partial_explicit.items():
        if departure in partial_departures:
            continue
        record = {stop: values.get(stop, "") for stop in config.partial_stops}
        source = {stop: ("full" if stop in values else "not_served") for stop in config.partial_stops}
        services.append(
            _build_service(
                departure,
                record,
                source,
                source_url,
                config.partial_stops,
                config,
                None,
                ["Explicit service outside the frequency range"],
            )
        )

    services.sort(key=lambda service: to_minutes(service.departure))

    full_rule = FrequencyRule(
        rule_id=full_rule_id,
        source_text=f"{full_start} > {full_end} MAIZTASUNA FRECUENCIA {_format_interval(full_interval)} min",
        source_pdf=source_url,
        page=1,
        block=config.full_block,
        origin=config.full_origin,
        start=full_start,
        end=full_end,
        interval_minutes=full_interval,
        calendar="WD",
        expanded_service_ids=[
            service.service_id
            for service in services
            if full_rule_id in service.frequency_rule_ids
        ],
    )
    partial_rule = FrequencyRule(
        rule_id=partial_rule_id,
        source_text=f"{partial_start} > {partial_end} MAIZTASUNA FRECUENCIA "
        f"{_format_interval(partial_interval).replace('.', ',')} min",
        source_pdf=source_url,
        page=1,
        block=config.partial_block,
        origin=config.partial_origin,
        start=partial_start,
        end=partial_end,
        interval_minutes=partial_interval,
        calendar="WD",
        expanded_service_ids=[
            service.service_id
            for service in services
            if partial_rule_id in service.frequency_rule_ids
        ],
    )
    return services, [full_rule, partial_rule]


def parse_e2_weekday(
    pdf: str | Path, source_url: str = "T1 Hendaia - Lasarte/Oria"
) -> tuple[list[Service], list[FrequencyRule]]:
    return parse_e2_direction(pdf, source_url, FORWARD)


def parse_e2_reverse(
    pdf: str | Path, source_url: str = "T1 Lasarte/Oria - Hendaia"
) -> tuple[list[Service], list[FrequencyRule]]:
    return parse_e2_direction(pdf, source_url, REVERSE)
