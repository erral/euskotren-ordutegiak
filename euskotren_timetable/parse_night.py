"""Shared parser for the Saturday-night tables of E2/T1 and E4."""

from dataclasses import dataclass
from pathlib import Path

from .model import Service, StopTime
from .parse_e1 import is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E2_STOPS, E4_STOPS, stop_id

E2_REVERSE_STOPS = list(reversed(E2_STOPS))
# The E4 night block has both Amorebieta columns: the E1 Geltokia and the
# E4 Geralekua. The E4 day tables only have Geralekua.
E4_NIGHT_STOPS = E4_STOPS[:13] + ["Amorebieta Geltokia"] + E4_STOPS[13:]
E4_REVERSE_STOPS = list(reversed(E4_NIGHT_STOPS))


@dataclass(frozen=True)
class NightTableConfig:
    primary_line: str
    direction: str
    slug: str
    stops_order: list[str]
    grid_stops: list[str]
    grid_rows: tuple[float, float, float, float, int, float]
    night_rows: tuple[float, float, float, float, int, float]
    block: str


def from_minutes_extended(value: int) -> str:
    return f"{value // 60}:{value % 60:02d}"


def extend_times(values: list[tuple[str, str]]) -> list[tuple[str, int, str]]:
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


def parse_night_table(pdf: str | Path, source_url: str, config: NightTableConfig) -> list[Service]:
    words = words_from_pdf(pdf, page=1)
    grid_rows = cluster_rows(words, *config.grid_rows)
    complete = [row for row in grid_rows if len(row) == len(config.grid_stops)]
    if not complete:
        raise ValueError(f"{config.block}: full-line header not found")
    grid = build_grid(complete[0], config.grid_stops)

    rows = cluster_rows(words, *config.night_rows)
    services: list[Service] = []
    for row in rows:
        values = row_to_dict(row, grid)
        timed = [(stop, values[stop]) for stop in config.grid_stops if is_time(values.get(stop))]
        if len(timed) < 2:
            continue
        extended = extend_times(timed)
        by_stop = {stop: (offset, time) for stop, offset, time in extended}
        origin, departure = extended[0][0], extended[0][2]
        destination, arrival = extended[-1][0], extended[-1][2]

        stop_times: list[StopTime] = []
        for sequence, stop in enumerate(config.stops_order, 1):
            value = values.get(stop, "")
            if stop in by_stop:
                offset, time = by_stop[stop]
                stop_times.append(
                    StopTime(stop_id(stop), stop, sequence, time, "stop", "night", offset)
                )
            elif value == ">":
                stop_times.append(StopTime(stop_id(stop), stop, sequence, None, "pass", "night", 0))
            elif value == "-":
                stop_times.append(
                    StopTime(stop_id(stop), stop, sequence, None, "not_served", "night", 0)
                )
            else:
                stop_times.append(
                    StopTime(stop_id(stop), stop, sequence, None, "not_served", "not_served", 0)
                )

        services.append(
            Service(
                service_id=(
                    f"{config.primary_line}-{config.slug}-SN-{departure.replace(':', '').zfill(4)}"
                ),
                primary_line=config.primary_line,
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


E2_FORWARD = NightTableConfig(
    primary_line="E2-T1",
    direction="Hendaia-Lasarte",
    slug="HENDAIA-LASARTE",
    stops_order=E2_STOPS,
    grid_stops=E2_STOPS,
    grid_rows=(40, 900, 1000, 1160, 23, 120),
    night_rows=(40, 900, 1000, 1160, 23, 120),
    block="E2-T1 Hendaia -> Lasarte-Oria Saturday night",
)

E2_REVERSE = NightTableConfig(
    primary_line="E2-T1",
    direction="Lasarte-Hendaia",
    slug="LASARTE-HENDAIA",
    stops_order=E2_REVERSE_STOPS,
    grid_stops=E2_REVERSE_STOPS,
    grid_rows=(40, 900, 990, 1140, 23, 120),
    night_rows=(40, 900, 990, 1140, 23, 120),
    block="E2-T1 Lasarte-Oria -> Hendaia Saturday night",
)

E4_FORWARD = NightTableConfig(
    primary_line="E4",
    direction="Matiko-Bermeo",
    slug="MATIKO-BERMEO",
    stops_order=E4_NIGHT_STOPS,
    grid_stops=E4_NIGHT_STOPS,
    grid_rows=(400, 1400, 1040, 1150, 25, 450),
    night_rows=(400, 1400, 1040, 1150, 25, 450),
    block="E4 Matiko -> Bermeo Saturday night",
)

E4_REVERSE = NightTableConfig(
    primary_line="E4",
    direction="Bermeo-Matiko",
    slug="BERMEO-MATIKO",
    stops_order=E4_REVERSE_STOPS,
    grid_stops=E4_REVERSE_STOPS,
    grid_rows=(400, 1400, 1845, 1940, 25, 450),
    night_rows=(400, 1400, 1845, 1940, 25, 450),
    block="E4 Bermeo -> Matiko Saturday night",
)


def parse_e2_night(pdf: str | Path, source_url: str = "T1 night") -> list[Service]:
    return parse_night_table(pdf, source_url, E2_FORWARD)


def parse_e2_night_reverse(pdf: str | Path, source_url: str = "T1 night") -> list[Service]:
    return parse_night_table(pdf, source_url, E2_REVERSE)


def parse_e4_night(pdf: str | Path, source_url: str = "E4 night") -> list[Service]:
    return parse_night_table(pdf, source_url, E4_FORWARD)


def parse_e4_night_reverse(pdf: str | Path, source_url: str = "E4 night") -> list[Service]:
    return parse_night_table(pdf, source_url, E4_REVERSE)
