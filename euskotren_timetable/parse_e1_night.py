"""Parse the E1 Saturday-night (Noches del sábado al domingo) tables.

The night blocks are partial Deba-Matiko / Matiko-Deba tables. Times after
midnight are stored with an extended clock (24:xx, 25:xx, ...) and the
``day_offset`` field marks the calendar day.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import Service, StopTime
from .parse_e1 import is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, E1_STOPS, stop_id

E1_REVERSE_FULL_42 = list(reversed(E1_FULL_42))
E1_REVERSE_STOPS = list(reversed(E1_STOPS))


@dataclass(frozen=True)
class NightConfig:
    direction: str
    slug: str
    stops_42: list[str]
    stops_50: list[str]
    rows: tuple[float, float, float, float, int, float]
    block: str


FORWARD = NightConfig(
    direction="Pasaia-Matiko",
    slug="PASAIA-MATIKO",
    stops_42=E1_FULL_42,
    stops_50=E1_STOPS,
    rows=(50, 1420, 790, 870, 10, 700),
    block="E1 Pasaia -> Matiko Saturday night",
)

REVERSE = NightConfig(
    direction="Matiko-Pasaia",
    slug="MATIKO-PASAIA",
    stops_42=E1_REVERSE_FULL_42,
    stops_50=E1_REVERSE_STOPS,
    rows=(50, 1420, 780, 865, 10, 110),
    block="E1 Matiko -> Pasaia Saturday night",
)


def from_minutes_extended(value: int) -> str:
    return f"{value // 60}:{value % 60:02d}"


def _extend_times(
    values: list[tuple[str, str]]
) -> list[tuple[str, int, str]]:
    """Return (stop, day_offset, extended_time) for one night row."""
    if not values:
        return []
    offset = 1 if to_minutes(values[0][1]) < 12 * 60 else 0
    previous = None
    out: list[tuple[str, int, str]] = []
    for stop, value in values:
        base = to_minutes(value)
        if previous is not None and base < previous - 12 * 60:
            offset += 1
        out.append((stop, offset, from_minutes_extended(base + 1440 * offset)))
        previous = base
    return out


def parse_e1_night_direction(
    pdf: str | Path, source_url: str, config: NightConfig
) -> list[Service]:
    words = words_from_pdf(pdf, page=1)
    full_rows = cluster_rows(words, 40, 1420, 430, 570, 20, 110)
    if not full_rows:
        raise ValueError("could not find the E1 full-line header")
    grid = build_grid(full_rows[0], config.stops_42)

    night_rows = cluster_rows(words, *config.rows)
    if not night_rows:
        raise ValueError(f"could not find the E1 night table: {config.block}")

    services: list[Service] = []
    for row in night_rows:
        values = row_to_dict(row, grid)
        timed = [
            (stop, values[stop])
            for stop in config.stops_42
            if is_time(values.get(stop))
        ]
        if not timed:
            continue
        extended = _extend_times(timed)
        by_stop = {stop: (offset, time) for stop, offset, time in extended}
        origin, departure = extended[0][0], extended[0][2]
        destination, arrival = extended[-1][0], extended[-1][2]

        stop_times: list[StopTime] = []
        for sequence, stop in enumerate(config.stops_50, 1):
            if stop in by_stop:
                offset, time = by_stop[stop]
                stop_times.append(
                    StopTime(
                        stop_id(stop),
                        stop,
                        sequence,
                        time,
                        "stop",
                        "night",
                        offset,
                    )
                )
            else:
                stop_times.append(
                    StopTime(
                        stop_id(stop),
                        stop,
                        sequence,
                        None,
                        "not_served",
                        "not_served",
                        0,
                    )
                )

        services.append(
            Service(
                service_id=(
                    f"E1-{config.slug}-SN-"
                    f"{departure.replace(':', '').zfill(4)}"
                ),
                primary_line="E1",
                pattern=["night"],
                direction=config.direction,
                calendar="SN",
                valid_from="2026-11-21",
                valid_to=None,
                origin=origin,
                destination=destination,
                departure=departure,
                arrival=arrival,
                source_pdf=source_url,
                frequency_rule_ids=[],
                notes=["Saturday night (Noches del sábado al domingo)"],
                appears_in=[],
                stop_times=stop_times,
            )
        )

    services.sort(key=lambda service: to_minutes(service.departure))
    return services


def parse_e1_night(
    pdf: str | Path, source_url: str = "E1 Pasaia - Matiko night"
) -> list[Service]:
    return parse_e1_night_direction(pdf, source_url, FORWARD)


def parse_e1_night_reverse(
    pdf: str | Path, source_url: str = "E1 Matiko - Pasaia night"
) -> list[Service]:
    return parse_e1_night_direction(pdf, source_url, REVERSE)
