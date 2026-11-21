"""Parse the E4 Matiko <-> Bermeo weekday full-line timetables.

The E4 poster also contains weekend/night tables and short-turn/transfer
services that start at Amorebieta Geltokia (a leading `-` at Bermeo/Matiko).
This slice parses the full-line weekday tables only; those transfer short-turns
are deferred.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E4_STOPS, stop_id

TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
E4_REVERSE_STOPS = list(reversed(E4_STOPS))


@dataclass(frozen=True)
class E4Config:
    stops: list[str]
    origin: str
    end: str
    direction: str
    slug: str
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str
    calendar: str = "WD"
    frequency_label: str = "30-minute frequency"


FORWARD = E4Config(
    stops=E4_STOPS,
    origin="Matiko-Bilbao",
    end="Bermeo",
    direction="Matiko-Bermeo",
    slug="MATIKO-BERMEO",
    rows=(400, 1350, 480, 700, 20, 430),
    note=(560, 585, 800, 815, 700, 1050),
    block="E4 Matiko -> Bermeo weekday",
)

REVERSE = E4Config(
    stops=E4_REVERSE_STOPS,
    origin="Bermeo",
    end="Matiko-Bilbao",
    direction="Bermeo-Matiko",
    slug="BERMEO-MATIKO",
    rows=(400, 1350, 1340, 1540, 20, 430),
    note=(1428, 1450, 805, 820, 700, 1050),
    block="E4 Bermeo -> Matiko weekday",
)

WEEKEND_FORWARD = E4Config(
    stops=E4_STOPS,
    origin="Matiko-Bilbao",
    end="Bermeo",
    direction="Matiko-Bermeo",
    slug="MATIKO-BERMEO",
    rows=(400, 1400, 780, 910, 15, 480),
    note=(810, 830, 810, 835, 700, 1050),
    block="E4 Matiko -> Bermeo weekend",
    calendar="WE",
    frequency_label="60-minute frequency",
)

WEEKEND_REVERSE = E4Config(
    stops=E4_REVERSE_STOPS,
    origin="Bermeo",
    end="Matiko-Bilbao",
    direction="Bermeo-Matiko",
    slug="BERMEO-MATIKO",
    rows=(400, 1400, 1600, 1715, 15, 480),
    note=(1635, 1655, 810, 835, 700, 1050),
    block="E4 Bermeo -> Matiko weekend",
    calendar="WE",
    frequency_label="60-minute frequency",
)


GERNIKA_WD_FORWARD = E4Config(
    stops=E4_STOPS,
    origin="Matiko-Bilbao",
    end="Bermeo",
    direction="Matiko-Bermeo",
    slug="MATIKO-BERMEO",
    rows=(400, 1400, 420, 490, 20, 480),
    note=(0, 0, 0, 0, 0, 0),
    block="E4 Gernika -> Bermeo weekday short-turn",
    calendar="WD",
)

GERNIKA_WE_FORWARD = E4Config(
    stops=E4_STOPS,
    origin="Matiko-Bilbao",
    end="Bermeo",
    direction="Matiko-Bermeo",
    slug="MATIKO-BERMEO",
    rows=(400, 1400, 720, 780, 20, 480),
    note=(0, 0, 0, 0, 0, 0),
    block="E4 Gernika -> Bermeo weekend short-turn",
    calendar="WE",
)

GERNIKA_WD_REVERSE = E4Config(
    stops=E4_REVERSE_STOPS,
    origin="Bermeo",
    end="Matiko-Bilbao",
    direction="Bermeo-Matiko",
    slug="BERMEO-MATIKO",
    rows=(400, 1400, 1340, 1380, 20, 480),
    note=(0, 0, 0, 0, 0, 0),
    block="E4 Gernika -> Matiko weekday short-turn",
    calendar="WD",
)

GERNIKA_WE_REVERSE = E4Config(
    stops=E4_REVERSE_STOPS,
    origin="Bermeo",
    end="Matiko-Bilbao",
    direction="Bermeo-Matiko",
    slug="BERMEO-MATIKO",
    rows=(400, 1400, 1560, 1600, 20, 480),
    note=(0, 0, 0, 0, 0, 0),
    block="E4 Gernika -> Matiko weekend short-turn",
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


def _parse_note(words, config: E4Config) -> tuple[str, str, int]:
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
    raise ValueError("E4 frequency note not found")


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
    config: E4Config,
    frequency_rule_id: str | None,
    extra_notes: list[str] | None = None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    is_full = is_time(record.get(config.end))
    pattern = ["full"] if is_full else ["short-turn"]
    notes: list[str] = []
    if frequency_rule_id:
        notes.append(f"{config.frequency_label} {frequency_rule_id}")
    elif not is_full:
        notes.append(f"Explicit short-turn to {destination}")
    else:
        notes.append("Explicit service outside the frequency range")
    if config.calendar == "WE":
        notes.insert(0, "Weekend (Saturday, Sunday + holiday)")
    if extra_notes:
        notes.extend(extra_notes)

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
        service_id=f"E4-{config.slug}-{config.calendar}-{departure.replace(':', '').zfill(4)}",
        primary_line="E4",
        pattern=pattern,
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


def parse_e4_direction(
    pdf: str | Path, source_url: str, config: E4Config
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    if not rows:
        raise ValueError("E4 table rows not found")

    grid = build_grid(next(row for row in rows if len(row) == len(config.stops)), config.stops)
    explicit = {}
    inferred_origin: set[str] = set()
    for row in rows:
        values = row_to_dict(row, grid)
        if (
            config.calendar == "WE"
            and config.direction == "Matiko-Bermeo"
            and not is_time(values.get(config.origin))
            and is_time(values.get("Uribarri (Bilbao)"))
            and values.get("Bermeo") == "-"
            and is_time(values.get("Gernika"))
        ):
            values[config.origin] = add_minutes(values["Uribarri (Bilbao)"], -1)
            inferred_origin.add(values[config.origin])
        if is_time(values.get(config.origin)):
            explicit[values[config.origin]] = values
    if not explicit:
        raise ValueError("E4 full-line row not found")

    start, end, interval = _parse_note(words, config)
    rule_id = (
        f"E4-{config.calendar}-{start.replace(':', '').zfill(4)}-"
        f"{end.replace(':', '').zfill(4)}-{interval}"
    )
    template = explicit[start]
    generated = _generate(start, end, interval)

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
        extra = None
        if departure in inferred_origin:
            extra = [
                "22:12 Sunday/holiday Gernika variant",
                "Matiko time inferred as 22:12 from the source note",
            ]
        service = _build_service(
            departure, record, source, source_url, config, None, extra_notes=extra
        )
        if departure in inferred_origin:
            # The source note restricts the Gernika variant to Sundays/holidays.
            service.calendar = "SU"
            service.service_id = (
                f"E4-{config.slug}-SU-{departure.replace(':', '').zfill(4)}"
            )
            service.notes = [
                "Sunday + holiday" if note == "Weekend (Saturday, Sunday + holiday)" else note
                for note in service.notes
            ]
        services.append(service)

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=f"{start} > {end} MAIZTASUNA FRECUENCIA {interval} min",
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


def parse_e4_gernika_turns(
    pdf: str | Path, source_url: str, config: E4Config
) -> list[Service]:
    """Include the Gernika-origin rows (leading ``-`` at Matiko/Bermeo)."""
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    grid_row = next((row for row in rows if len(row) == len(config.stops)), None)
    if grid_row is None:
        return []
    grid = build_grid(grid_row, config.stops)

    services: list[Service] = []
    for row in rows:
        values = row_to_dict(row, grid)
        if is_time(values.get(config.origin)):
            continue
        timed = [
            (stop, values[stop])
            for stop in config.stops
            if is_time(values.get(stop))
        ]
        if not timed or timed[0][0] != "Gernika":
            continue
        record = {stop: values.get(stop, "") for stop in config.stops}
        source = {
            stop: ("full" if stop in values else "not_served")
            for stop in config.stops
        }
        service = _build_service(
            timed[0][1], record, source, source_url, config, None
        )
        service.pattern = ["short-turn"]
        service.notes = [
            "Weekend (Saturday, Sunday + holiday)"
            if config.calendar == "WE"
            else "Weekday",
            "Gernika short-turn",
        ]
        services.append(service)
    services.sort(key=lambda service: to_minutes(service.departure))
    return services


def parse_e4_weekday(
    pdf: str | Path, source_url: str = "E4 Bilbao-Bermeo"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e4_direction(pdf, source_url, FORWARD)


def parse_e4_reverse(
    pdf: str | Path, source_url: str = "E4 Bermeo-Bilbao"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e4_direction(pdf, source_url, REVERSE)


def parse_e4_weekend(
    pdf: str | Path, source_url: str = "E4 Matiko-Bermeo weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e4_direction(pdf, source_url, WEEKEND_FORWARD)


def parse_e4_weekend_reverse(
    pdf: str | Path, source_url: str = "E4 Bermeo-Matiko weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e4_direction(pdf, source_url, WEEKEND_REVERSE)
