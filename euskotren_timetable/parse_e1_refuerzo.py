"""Parse the E1 ``Zerbitzu gehigarriak`` refuerzo tables.

These are explicit-only weekday services:
- Zaldibar -> Matiko
- Matiko -> Traña
"""

from dataclasses import dataclass
from pathlib import Path

from .model import Service, StopTime
from .parse_e1 import from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, stop_id

E1_REVERSE_42 = list(reversed(E1_FULL_42))
ZALDIbar_MATIKO_STOPS = E1_FULL_42[23:]
MATIKO_TRANA_STOPS = E1_REVERSE_42[:17]


@dataclass(frozen=True)
class RefuerzoConfig:
    stops: list[str]
    direction: str
    slug: str
    rows: tuple[float, float, float, float, int, float]
    block: str


FORWARD = RefuerzoConfig(
    stops=ZALDIbar_MATIKO_STOPS,
    direction="Pasaia-Matiko",
    slug="ZALDIBAR-MATIKO",
    rows=(40, 650, 1490, 1700, 19, 120),
    block="E1 Zaldibar -> Matiko refuerzo",
)

REVERSE = RefuerzoConfig(
    stops=MATIKO_TRANA_STOPS,
    direction="Matiko-Pasaia",
    slug="MATIKO-TRANA",
    rows=(40, 650, 1470, 1700, 16, 120),
    block="E1 Matiko -> Traña refuerzo",
)


def parse_refuerzo(
    pdf: str | Path, source_url: str, config: RefuerzoConfig
) -> list[Service]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    complete = [row for row in rows if len(row) <= len(config.stops)]
    grid_row = next(
        (row for row in complete if len(row) == len(config.stops)), None
    )
    if grid_row is None:
        raise ValueError(f"{config.block}: no complete rows")

    grid = build_grid(grid_row, config.stops)
    services: list[Service] = []
    for row in complete:
        record = row_to_dict(row, grid)
        timed = [
            (stop, record[stop])
            for stop in config.stops
            if is_time(record.get(stop))
        ]
        if len(timed) < 2:
            continue
        origin, departure = timed[0]
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
                StopTime(stop_id(stop), stop, sequence, time, disposition, "refuerzo")
            )

        services.append(
            Service(
                service_id=(
                    f"E1-{config.slug}-WD-"
                    f"{departure.replace(':', '').zfill(4)}"
                ),
                primary_line="E1",
                pattern=["refuerzo"],
                direction=config.direction,
                calendar="WD",
                valid_from="2026-11-21",
                valid_to=None,
                origin=origin,
                destination=destination,
                departure=from_minutes(to_minutes(departure)),
                arrival=from_minutes(to_minutes(arrival)),
                source_pdf=source_url,
                frequency_rule_ids=[],
                notes=["Zerbitzu gehigarriak / Servicios de refuerzo"],
                appears_in=[],
                stop_times=stop_times,
            )
        )

    services.sort(key=lambda service: to_minutes(service.departure))
    return services


def parse_e1_refuerzos(
    forward_pdf: str | Path,
    reverse_pdf: str | Path,
    forward_url: str = "E1 refuerzos",
    reverse_url: str = "E1 refuerzos",
) -> list[Service]:
    return (
        parse_refuerzo(forward_pdf, forward_url, FORWARD)
        + parse_refuerzo(reverse_pdf, reverse_url, REVERSE)
    )
