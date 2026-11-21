"""Parse the E2/T1 Saturday and Sunday Añorga shuttle tables.

The full-line weekend is a separate combined ``WE`` table. The Pasaia-Añorga
shuttle has its own Saturday and Sunday/holiday blocks, with 7.5-minute,
15-minute and hourly sub-ranges.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .parse_e2 import (
    E2_PARTIAL,
    _format_interval,
    generate_cyclic,
    generate_fixed,
    parse_frequency_note,
)
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import stop_id

E2_REVERSE_PARTIAL = list(reversed(E2_PARTIAL))


@dataclass(frozen=True)
class ShuttleRange:
    note: tuple[float, float, float, float, float, float] = ()
    mode: str = "fixed"  # fixed | cycle | hourly
    cycle: tuple[int, ...] = ()
    head_y: tuple[float, float] = (0.0, 0.0)
    range_y: tuple[float, float, float, float] = ()  # hourly range: y0,y1,x0,x1


@dataclass(frozen=True)
class ShuttleBlock:
    stops: list[str]
    origin: str
    direction: str
    slug: str
    calendar: str
    rows: tuple[float, float, float, float, int, float]
    ranges: tuple[ShuttleRange, ...]
    block: str


FORWARD_SATURDAY = ShuttleBlock(
    stops=E2_PARTIAL,
    origin="Pasaia",
    direction="Hendaia-Lasarte",
    slug="PASAIA-ANORGA",
    calendar="SA",
    rows=(880, 1400, 920, 1160, 11, 920),
    ranges=(
        ShuttleRange(
            note=(1045, 1060, 950, 1100, 880, 1300),
            mode="cycle",
            cycle=(7, 8, 8, 7),
        ),
    ),
    block="E2-T1 Pasaia -> Anorga Saturday shuttle",
)

FORWARD_SUNDAY = ShuttleBlock(
    stops=E2_PARTIAL,
    origin="Pasaia",
    direction="Hendaia-Lasarte",
    slug="PASAIA-ANORGA",
    calendar="SU",
    rows=(880, 1400, 1200, 1560, 11, 920),
    ranges=(
        ShuttleRange(
            mode="hourly",
            head_y=(1200, 1330),
            range_y=(1328, 1338, 950, 1250),
        ),
        ShuttleRange(
            note=(1440, 1455, 950, 1100, 880, 1300),
            mode="cycle",
            cycle=(7, 8, 8, 7),
        ),
    ),
    block="E2-T1 Pasaia -> Anorga Sunday shuttle",
)

REVERSE_SATURDAY = ShuttleBlock(
    stops=E2_REVERSE_PARTIAL,
    origin="Añorga (Donostia)",
    direction="Lasarte-Hendaia",
    slug="ANORGA-PASAIA",
    calendar="SA",
    rows=(920, 1400, 960, 1160, 11, 940),
    ranges=(
        ShuttleRange(
            note=(1085, 1100, 980, 1120, 920, 1350),
            mode="cycle",
            cycle=(8, 7, 8, 7),
        ),
    ),
    block="E2-T1 Anorga -> Pasaia Saturday shuttle",
)

REVERSE_SUNDAY = ShuttleBlock(
    stops=E2_REVERSE_PARTIAL,
    origin="Añorga (Donostia)",
    direction="Lasarte-Hendaia",
    slug="ANORGA-PASAIA",
    calendar="SU",
    rows=(920, 1400, 1200, 1660, 11, 940),
    ranges=(
        ShuttleRange(
            note=(1280, 1295, 980, 1120, 920, 1350),
            mode="fixed",
        ),
        ShuttleRange(
            mode="hourly",
            head_y=(1300, 1400),
            range_y=(1406, 1416, 950, 1250),
        ),
        ShuttleRange(
            note=(1578, 1592, 980, 1120, 920, 1350),
            mode="cycle",
            cycle=(8, 7, 8, 7),
        ),
    ),
    block="E2-T1 Anorga -> Pasaia Sunday shuttle",
)


def parse_range_note(
    words: list[tuple[float, float, str]],
    y_min: float,
    y_max: float,
    x_min: float,
    x_max: float,
) -> tuple[str, str]:
    """Read a bare ``start > end`` note such as the hourly-repeat range."""
    times = [
        word
        for x, y, word in words
        if y_min <= y <= y_max and x_min <= x <= x_max and is_time(word)
    ]
    if len(times) < 2:
        raise ValueError("range note not found in the requested region")
    return times[0], times[1]


def _rule_id(config: ShuttleBlock, start: str, end: str, interval: float) -> str:
    return (
        f"E2-T1-{config.slug}-{config.calendar}-"
        f"{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-"
        f"{_format_interval(interval)}"
    )


def _service_id(config: ShuttleBlock, departure: str) -> str:
    return (
        f"E2-T1-{config.slug}-{config.calendar}-"
        f"{departure.replace(':', '').zfill(4)}"
    )


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: ShuttleBlock,
    rule_ids: list[str],
    notes: list[str],
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]

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
        service_id=_service_id(config, departure),
        primary_line="E2-T1",
        pattern=["short-turn"],
        direction=config.direction,
        calendar=config.calendar,
        valid_from="2026-11-21",
        valid_to=None,
        origin=origin,
        destination=destination,
        departure=from_minutes(to_minutes(origin_time)),
        arrival=from_minutes(to_minutes(arrival)),
        source_pdf=source_url,
        frequency_rule_ids=rule_ids,
        notes=notes,
        appears_in=[],
        stop_times=stop_times,
    )


def parse_e2_shuttle_block(
    pdf: str | Path, source_url: str, config: ShuttleBlock
) -> tuple[list[Service], list[FrequencyRule]]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    complete = [row for row in rows if len(row) == len(config.stops)]
    if not complete:
        raise ValueError(f"{config.block}: no complete rows")

    grid = build_grid(complete[0], config.stops)
    records: list[tuple[float, str, dict[str, str]]] = []
    for row in complete:
        record = row_to_dict(row, grid)
        departure = record.get(config.origin, "")
        if is_time(departure):
            records.append((row[0][1], departure, record))
    explicit = {departure: record for _y, departure, record in records}
    if not explicit:
        raise ValueError(f"{config.block}: no explicit rows")

    ordered = sorted(explicit, key=to_minutes)
    merged: dict[str, dict] = {}
    range_results: list[tuple[str, str, str, float, list[str], str]] = []

    def add(departure: str, record: dict[str, str], rule_id: str, note: str) -> None:
        entry = merged.setdefault(
            departure,
            {"record": {}, "source": {}, "rules": [], "notes": []},
        )
        entry["record"].update(record)
        for stop, value in record.items():
            entry["source"][stop] = "frequency"
        if rule_id not in entry["rules"]:
            entry["rules"].append(rule_id)
        if note not in entry["notes"]:
            entry["notes"].append(note)
        if departure in explicit:
            entry["record"].update(explicit[departure])
            for stop in explicit[departure]:
                entry["source"][stop] = "full"

    for shuttle_range in config.ranges:
        if shuttle_range.range_y:
            start, end = parse_range_note(words, *shuttle_range.range_y)
            interval = 60.0
        else:
            start, end, interval = parse_frequency_note(words, *shuttle_range.note)
        rule_id = _rule_id(config, start, end, interval)
        generated: list[str] = []

        if shuttle_range.mode == "fixed":
            departures = generate_fixed(start, end, interval)
            template_departure = start
            if template_departure not in explicit:
                template_departure = next(
                    departure for departure in ordered
                    if to_minutes(departure) >= to_minutes(start)
                )
            template = explicit[template_departure]
            for departure in departures:
                offset = to_minutes(departure) - to_minutes(template_departure)
                record = {
                    stop: add_minutes(template[stop], offset)
                    if is_time(template.get(stop))
                    else template.get(stop, "")
                    for stop in config.stops
                }
                add(departure, record, rule_id, f"{_format_interval(interval)}-minute frequency {rule_id}")
                generated.append(departure)
        elif shuttle_range.mode == "cycle":
            departures = generate_cyclic(start, end, list(shuttle_range.cycle))
            template_departure = start
            if template_departure not in explicit:
                template_departure = next(
                    departure for departure in ordered
                    if to_minutes(departure) >= to_minutes(start)
                )
            template = explicit[template_departure]
            for departure in departures:
                offset = to_minutes(departure) - to_minutes(template_departure)
                record = {
                    stop: add_minutes(template[stop], offset)
                    if is_time(template.get(stop))
                    else template.get(stop, "")
                    for stop in config.stops
                }
                add(departure, record, rule_id, f"7.5-minute frequency {rule_id}")
                generated.append(departure)
        else:  # hourly
            head = [
                record
                for y, departure, record in records
                if shuttle_range.head_y[0] <= y <= shuttle_range.head_y[1]
                and to_minutes(departure) >= to_minutes(start)
            ]
            if not head:
                raise ValueError(f"{config.block}: hourly pattern not found")
            head.sort(key=lambda record: to_minutes(record[config.origin]))
            base = to_minutes(head[0][config.origin])
            step = 60
            cycle = 0
            while base + step * cycle < to_minutes(end):
                offset = step * cycle
                for pattern in head:
                    departure = add_minutes(pattern[config.origin], offset)
                    record = {
                        stop: add_minutes(pattern[stop], offset)
                        if is_time(pattern.get(stop))
                        else pattern.get(stop, "")
                        for stop in config.stops
                    }
                    add(departure, record, rule_id, f"Hourly pattern {rule_id}")
                    generated.append(departure)
                cycle += 1

        range_results.append(
            (rule_id, start, end, interval, generated, config.block)
        )

    for departure, record in explicit.items():
        entry = merged.setdefault(
            departure,
            {"record": {}, "source": {}, "rules": [], "notes": []},
        )
        entry["record"].update(record)
        for stop, value in record.items():
            entry["source"][stop] = "full"
        if not entry["rules"]:
            entry["notes"].append("Explicit service outside the frequency range")

    services = [
        _build_service(
            departure,
            entry["record"],
            entry["source"],
            source_url,
            config,
            entry["rules"],
            entry["notes"],
        )
        for departure, entry in merged.items()
    ]
    services.sort(key=lambda service: to_minutes(service.departure))

    rules: list[FrequencyRule] = []
    for rule_id, start, end, interval, generated, block in range_results:
        rules.append(
            FrequencyRule(
                rule_id=rule_id,
                source_text=(
                    f"{start} > {end} MAIZTASUNA FRECUENCIA "
                    f"{_format_interval(interval)} min"
                ),
                source_pdf=source_url,
                page=1,
                block=block,
                origin=config.origin,
                start=start,
                end=end,
                interval_minutes=interval,
                calendar=config.calendar,
                expanded_service_ids=[
                    _service_id(config, departure)
                    for departure in generated
                ],
            )
        )
    return services, rules


def parse_e2_shuttle_weekend(
    forward_pdf: str | Path,
    reverse_pdf: str | Path,
    forward_url: str = "T1 Hendaia - Lasarte/Oria weekend shuttle",
    reverse_url: str = "T1 Lasarte/Oria - Hendaia weekend shuttle",
) -> tuple[list[Service], list[FrequencyRule]]:
    services: list[Service] = []
    rules: list[FrequencyRule] = []
    for pdf, url, config in (
        (forward_pdf, forward_url, FORWARD_SATURDAY),
        (forward_pdf, forward_url, FORWARD_SUNDAY),
        (reverse_pdf, reverse_url, REVERSE_SATURDAY),
        (reverse_pdf, reverse_url, REVERSE_SUNDAY),
    ):
        block_services, block_rules = parse_e2_shuttle_block(pdf, url, config)
        services.extend(block_services)
        rules.extend(block_rules)
    return services, rules
