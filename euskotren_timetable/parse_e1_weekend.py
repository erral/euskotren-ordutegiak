"""Parse the E1 combined weekend (Saturday + Sunday + holiday) full-line tables.

The E1 poster groups Saturday, Sunday and holidays into one block. This slice
parses the full-line tables in both directions; the eight shared Topo stops are
marked `?` because the weekend partial-table merge is deferred.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .parse_e2 import generate_fixed, parse_frequency_note
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, E1_STOPS, E1_TOP0_MISSING, stop_id

E1_REVERSE_42 = list(reversed(E1_FULL_42))
E1_REVERSE_STOPS = list(reversed(E1_STOPS))


@dataclass(frozen=True)
class WeekendConfig:
    stops_42: list[str]
    stops_50: list[str]
    origin: str
    direction: str
    slug: str
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str


FORWARD = WeekendConfig(
    stops_42=E1_FULL_42,
    stops_50=E1_STOPS,
    origin="Pasaia",
    direction="Pasaia-Matiko",
    slug="PASAIA-MATIKO",
    rows=(50, 1420, 600, 760, 40, 80),
    note=(680, 695, 680, 700, 600, 870),
    block="E1 Pasaia -> Matiko weekend",
)

REVERSE = WeekendConfig(
    stops_42=E1_REVERSE_42,
    stops_50=E1_REVERSE_STOPS,
    origin="Matiko-Bilbao",
    direction="Matiko-Pasaia",
    slug="MATIKO-PASAIA",
    rows=(50, 1420, 600, 760, 40, 80),
    note=(665, 685, 710, 730, 550, 900),
    block="E1 Matiko -> Pasaia weekend",
)


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: WeekendConfig,
    frequency_rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops_50 if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    notes = ["Weekend (Saturday, Sunday + holiday)"]
    notes.append(
        f"Hourly frequency {frequency_rule_id}"
        if frequency_rule_id
        else "Explicit service outside the frequency range"
    )

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(config.stops_50, 1):
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
        service_id=f"E1-{config.slug}-WE-{departure.replace(':', '').zfill(4)}",
        primary_line="E1",
        pattern=["through"],
        direction=config.direction,
        calendar="WE",
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


def parse_e1_weekend_direction(
    pdf: str | Path, source_url: str, config: WeekendConfig
) -> tuple[list[Service], FrequencyRule]:
    from .parse_e1_partial import (
        FORWARD_SATURDAY,
        FORWARD_SUNDAY,
        REVERSE_SATURDAY,
        REVERSE_SUNDAY,
        expand_partial_block,
        fill_service_from_partial,
    )

    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    if not rows:
        raise ValueError("E1 weekend rows not found")

    grid = build_grid(next(row for row in rows if len(row) == len(config.stops_42)), config.stops_42)
    explicit = {}
    for row in rows:
        values = row_to_dict(row, grid)
        if is_time(values.get(config.origin)):
            explicit[values[config.origin]] = values
    if not explicit:
        raise ValueError("E1 weekend full-line row not found")

    start, end, interval = parse_frequency_note(words, *config.note)
    rule_id = f"E1-WE-{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-{int(interval)}"
    template = explicit[start]
    generated = generate_fixed(start, end, interval)

    services: list[Service] = []
    for departure in generated:
        offset = to_minutes(departure) - to_minutes(start)
        record_42 = {
            stop: add_minutes(template[stop], offset) if is_time(template.get(stop)) else template.get(stop, "")
            for stop in config.stops_42
        }
        source_42 = {stop: "frequency" for stop in config.stops_42}
        if departure in explicit:
            for stop, value in explicit[departure].items():
                record_42[stop] = value
                source_42[stop] = "full"

        record = {}
        source = {}
        for stop in config.stops_50:
            if stop in record_42:
                record[stop] = record_42[stop]
                source[stop] = source_42[stop]
            else:
                record[stop] = "?"
                source[stop] = "unpublished"
        services.append(_build_service(departure, record, source, source_url, config, rule_id))

    for departure, values in explicit.items():
        if departure in generated:
            continue
        record_42 = {stop: values.get(stop, "") for stop in config.stops_42}
        record = {}
        source = {}
        for stop in config.stops_50:
            if stop in record_42:
                record[stop] = record_42[stop]
                source[stop] = "full"
            else:
                record[stop] = "?"
                source[stop] = "unpublished"
        services.append(_build_service(departure, record, source, source_url, config, None))

    if config.direction == "Pasaia-Matiko":
        saturday = expand_partial_block(words, FORWARD_SATURDAY)
        sunday = expand_partial_block(words, FORWARD_SUNDAY)
        key_stop = "Pasaia"
        note = (
            "Topo times from Pasaia-Zumaia weekend partial table; "
            "source side note: all trains stop Pasaia-Aia-Orio"
        )
    else:
        saturday = expand_partial_block(words, REVERSE_SATURDAY)
        sunday = expand_partial_block(words, REVERSE_SUNDAY)
        key_stop = "Zumaia"
        note = (
            "Topo times from Zumaia-Pasaia weekend partial table; "
            "source side note: all trains stop Aia-Orio-Pasaia"
        )
    partial = dict(sunday)
    partial.update(saturday)
    for service in services:
        fill_service_from_partial(
            service, partial, key_stop, E1_TOP0_MISSING, note
        )

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=f"{start} > {end} MAIZTASUNA FRECUENCIA {int(interval) // 60} h",
        source_pdf=source_url,
        page=1,
        block=config.block,
        origin=config.origin,
        start=start,
        end=end,
        interval_minutes=interval,
        calendar="WE",
        expanded_service_ids=[
            service.service_id for service in services if rule_id in service.frequency_rule_ids
        ],
    )
    return services, rule


def parse_e1_weekend(
    pdf: str | Path, source_url: str = "E1 Pasaia - Matiko weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e1_weekend_direction(pdf, source_url, FORWARD)


def parse_e1_weekend_reverse(
    pdf: str | Path, source_url: str = "E1 Matiko - Pasaia weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e1_weekend_direction(pdf, source_url, REVERSE)
