"""Merge the E1 Pasaia-Zumaia / Zumaia-Pasaia partial tables.

The full-line E1 posters omit the eight Topo stops between Pasaia and
Aia-Orio. A side note says every train serves them, and the partial
``Pasaia -> Zumaia`` / ``Zumaia -> Pasaia`` tables publish the missing times.
This module expands those partial tables and fills the omitted stops on the
matching full-line services without overwriting published full-line times.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .parse_e2 import generate_fixed, parse_frequency_note
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_PARTIAL_17, stop_id

E1_REVERSE_PARTIAL_17 = list(reversed(E1_PARTIAL_17))


@dataclass(frozen=True)
class PartialBlockConfig:
    stops: list[str]
    origin: str
    rows: tuple[float, float, float, float, int, float]
    note_regions: tuple[tuple[float, float, float, float, float, float], ...]
    calendar: str
    block: str


FORWARD_WEEKDAY = PartialBlockConfig(
    stops=E1_PARTIAL_17,
    origin="Pasaia",
    rows=(650, 1420, 1620, 1700, 17, 700),
    note_regions=((1655, 1670, 900, 1050, 700, 1200),),
    calendar="WD",
    block="E1 Pasaia -> Zumaia partial weekday",
)

FORWARD_SATURDAY = PartialBlockConfig(
    stops=E1_PARTIAL_17,
    origin="Pasaia",
    rows=(650, 1420, 1711, 1806, 17, 700),
    note_regions=((1750, 1765, 900, 1050, 700, 1200),),
    calendar="SA",
    block="E1 Pasaia -> Zumaia partial Saturday",
)

FORWARD_SUNDAY = PartialBlockConfig(
    stops=E1_PARTIAL_17,
    origin="Pasaia",
    rows=(650, 1420, 1808, 1960, 17, 700),
    note_regions=(
        (1848, 1862, 900, 1050, 700, 1200),
        (1896, 1910, 900, 1050, 700, 1200),
    ),
    calendar="SU",
    block="E1 Pasaia -> Zumaia partial Sunday",
)

REVERSE_WEEKDAY = PartialBlockConfig(
    stops=E1_REVERSE_PARTIAL_17,
    origin="Zumaia",
    rows=(700, 1420, 1600, 1690, 17, 730),
    note_regions=((1646, 1660, 900, 1050, 700, 1200),),
    calendar="WD",
    block="E1 Zumaia -> Pasaia partial weekday",
)

REVERSE_SATURDAY = PartialBlockConfig(
    stops=E1_REVERSE_PARTIAL_17,
    origin="Zumaia",
    rows=(700, 1420, 1737, 1810, 17, 730),
    note_regions=((1770, 1784, 900, 1050, 700, 1200),),
    calendar="SA",
    block="E1 Zumaia -> Pasaia partial Saturday",
)

REVERSE_SUNDAY = PartialBlockConfig(
    stops=E1_REVERSE_PARTIAL_17,
    origin="Zumaia",
    rows=(700, 1420, 1818, 1960, 17, 730),
    note_regions=(
        (1851, 1865, 900, 1050, 700, 1200),
        (1906, 1920, 900, 1050, 700, 1200),
    ),
    calendar="SU",
    block="E1 Zumaia -> Pasaia partial Sunday",
)


def expand_partial_block(
    words: list[tuple[float, float, str]], config: PartialBlockConfig
) -> dict[str, dict[str, str]]:
    """Return every partial service keyed by its origin departure time."""
    rows = cluster_rows(words, *config.rows)
    complete = [row for row in rows if len(row) == len(config.stops)]
    if not complete:
        return {}

    grid = build_grid(complete[0], config.stops)
    explicit: dict[str, dict[str, str]] = {}
    for row in complete:
        record = row_to_dict(row, grid)
        departure = record.get(config.origin, "")
        if is_time(departure):
            explicit[departure] = record
    if not explicit:
        return {}

    ordered = sorted(explicit, key=to_minutes)
    out: dict[str, dict[str, str]] = {}
    for note_region in config.note_regions:
        start, end, interval = parse_frequency_note(words, *note_region)
        template_departure = start
        if template_departure not in explicit:
            template_departure = next(
                departure for departure in ordered if to_minutes(departure) >= to_minutes(start)
            )
        template = explicit[template_departure]
        for departure in generate_fixed(start, end, interval):
            offset = to_minutes(departure) - to_minutes(template_departure)
            record = {
                stop: add_minutes(template[stop], offset)
                if is_time(template.get(stop))
                else template.get(stop, "")
                for stop in config.stops
            }
            if departure in explicit:
                record.update(explicit[departure])
            out[departure] = record

    # The source sometimes prints a boundary row one minute off the stated
    # frequency end (e.g. 22:31 against a 22:30 range end). Treat the explicit
    # row as the same service and drop the generated minute.
    for departure in list(out):
        if departure in explicit:
            continue
        if any(
            abs(to_minutes(departure) - to_minutes(explicit_departure)) <= 2
            for explicit_departure in explicit
        ):
            del out[departure]

    for departure, record in explicit.items():
        out.setdefault(departure, record)
    return out


def partial_map(pdf: str | Path, config: PartialBlockConfig) -> dict[str, dict[str, str]]:
    return expand_partial_block(words_from_pdf(pdf, page=1), config)


def build_partial_services(
    pdf: str | Path,
    source_url: str,
    config: PartialBlockConfig,
    full_line_times: set[str],
    direction: str,
    slug: str,
) -> list[Service]:
    """Build the short-turn services that are not full-line trains.

    The Pasaia-Zumaia / Zumaia-Pasaia tables contain both the full-line trains
    (which continue beyond Zumaia/Pasaia) and the short-turns. Times that match
    a full-line service are skipped to avoid duplicates.
    """
    records = expand_partial_block(words_from_pdf(pdf, page=1), config)
    services: list[Service] = []
    for departure, record in records.items():
        if departure in full_line_times:
            continue
        timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
        if len(timed) < 2:
            continue
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
            stop_times.append(StopTime(stop_id(stop), stop, sequence, time, disposition, "partial"))

        services.append(
            Service(
                service_id=(f"E1-{slug}-{config.calendar}-{departure.replace(':', '').zfill(4)}"),
                primary_line="E1",
                pattern=["short-turn"],
                direction=direction,
                calendar=config.calendar,
                valid_from="2026-11-21",
                valid_to=None,
                origin=origin,
                destination=destination,
                departure=from_minutes(to_minutes(origin_time)),
                arrival=from_minutes(to_minutes(arrival)),
                source_pdf=source_url,
                frequency_rule_ids=[],
                notes=[f"{slug.replace('-', ' ').title()} refuerzo"],
                appears_in=[],
                stop_times=stop_times,
            )
        )
    services.sort(key=lambda service: to_minutes(service.departure))
    return services


def fill_service_from_partial(
    service: Service,
    partial: dict[str, dict[str, str]],
    key_stop: str,
    fill_stops: list[str],
    note: str,
) -> int:
    """Fill unpublished stops from the matching partial row.

    Published full-line times always win; only ``?``/missing stops are filled.
    Returns the number of stops filled.
    """
    key_time = None
    for stop_time in service.stop_times:
        if stop_time.stop_name == key_stop and is_time(stop_time.time):
            key_time = stop_time.time
            break
    if key_time is None or key_time not in partial:
        return 0

    record = partial[key_time]
    filled = 0
    for stop_time in service.stop_times:
        if stop_time.stop_name not in fill_stops or is_time(stop_time.time):
            continue
        value = record.get(stop_time.stop_name)
        if is_time(value):
            stop_time.time = value
            stop_time.disposition = "stop"
            stop_time.source = "partial"
            filled += 1

    if filled and note not in service.notes:
        service.notes.append(note)
    return filled
