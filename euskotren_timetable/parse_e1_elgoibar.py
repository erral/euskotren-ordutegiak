"""Parse the Elgoibar <-> Matiko partial tables (Elgoibar-origin rows).

The combined table also carries Eibar-origin and Eibar-Ermua rows; this slice
adds the through Elgoibar/Matiko partials, which use fixed 30-minute / hourly
ranges.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, stop_id

E1_REVERSE_42 = list(reversed(E1_FULL_42))
ELGOIBAR_MATIKO_STOPS = E1_FULL_42[14:]
MATIKO_ELGOIBAR_STOPS = E1_REVERSE_42[:28]


@dataclass(frozen=True)
class ElgoibarConfig:
    stops: list[str]
    origin: str
    direction: str
    slug: str
    calendar: str
    rows: tuple[float, float, float, float, int, float]
    ranges: tuple[tuple[str, str, int], ...]
    block: str


WD_FORWARD = ElgoibarConfig(
    stops=ELGOIBAR_MATIKO_STOPS,
    origin="Elgoibar",
    direction="Pasaia-Matiko",
    slug="ELGOIBAR-MATIKO",
    calendar="WD",
    rows=(40, 1000, 1000, 1300, 28, 120),
    ranges=(("7:01", "17:01", 30), ("17:01", "21:01", 60)),
    block="E1 Elgoibar -> Matiko weekday",
)

WE_FORWARD = ElgoibarConfig(
    stops=ELGOIBAR_MATIKO_STOPS,
    origin="Elgoibar",
    direction="Pasaia-Matiko",
    slug="ELGOIBAR-MATIKO",
    calendar="WE",
    rows=(40, 1000, 1300, 1470, 28, 120),
    ranges=(("9:01", "22:01", 60),),
    block="E1 Elgoibar -> Matiko weekend",
)

WD_REVERSE = ElgoibarConfig(
    stops=MATIKO_ELGOIBAR_STOPS,
    origin="Matiko-Bilbao",
    direction="Matiko-Pasaia",
    slug="MATIKO-ELGOIBAR",
    calendar="WD",
    rows=(40, 1000, 1000, 1300, 28, 120),
    ranges=(("5:55", "14:55", 30), ("14:55", "20:25", 60)),
    block="E1 Matiko -> Elgoibar weekday",
)

WE_REVERSE = ElgoibarConfig(
    stops=MATIKO_ELGOIBAR_STOPS,
    origin="Matiko-Bilbao",
    direction="Matiko-Pasaia",
    slug="MATIKO-ELGOIBAR",
    calendar="WE",
    rows=(40, 1000, 1300, 1470, 28, 120),
    ranges=(("6:52", "19:52", 60),),
    block="E1 Matiko -> Elgoibar weekend",
)


def _generate(start: str, end: str, interval: int) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    while current <= last:
        out.append(from_minutes(current))
        current += interval
    return out


def _build(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: ElgoibarConfig,
    rule_id: str | None,
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

    notes = (
        [f"Frequency {rule_id}"] if rule_id
        else ["Explicit partial outside the frequency range"]
    )
    if config.calendar == "WE":
        notes.insert(0, "Weekend (Saturday, Sunday + holiday)")

    return Service(
        service_id=(
            f"E1-{config.slug}-{config.calendar}-"
            f"{departure.replace(':', '').zfill(4)}"
        ),
        primary_line="E1",
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
        frequency_rule_ids=[rule_id] if rule_id else [],
        notes=notes,
        appears_in=[],
        stop_times=stop_times,
    )


def parse_elgoibar_table(
    pdf: str | Path, source_url: str, config: ElgoibarConfig
) -> list[Service]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    explicit: dict[str, dict[str, str]] = {}
    template: dict[str, str] | None = None
    for row in rows:
        if len(row) != len(config.stops):
            continue
        grid = build_grid(row, config.stops)
        values = row_to_dict(row, grid)
        departure = values.get(config.origin, "")
        if not is_time(departure):
            continue
        explicit[departure] = values
        if template is None:
            template = values
    if template is None:
        raise ValueError(f"{config.block}: no complete rows")

    services: list[Service] = []
    generated: set[str] = set()
    for start, end, interval in config.ranges:
        rule_id = (
            f"E1-{config.slug}-{config.calendar}-"
            f"{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-"
            f"{interval}"
        )
        range_template = explicit.get(start, template)
        for departure in _generate(start, end, interval):
            if departure in generated:
                continue
            offset = to_minutes(departure) - to_minutes(start)
            record = {
                stop: add_minutes(range_template[stop], offset)
                if is_time(range_template.get(stop))
                else range_template.get(stop, "")
                for stop in config.stops
            }
            source = {stop: "frequency" for stop in config.stops}
            if departure in explicit:
                for stop, value in explicit[departure].items():
                    record[stop] = value
                    source[stop] = "full"
            services.append(_build(departure, record, source, source_url, config, rule_id))
            generated.add(departure)

    for departure, values in explicit.items():
        if departure in generated:
            continue
        record = {stop: values.get(stop, "") for stop in config.stops}
        source = {stop: ("full" if stop in values else "not_served") for stop in config.stops}
        services.append(_build(departure, record, source, source_url, config, None))

    services.sort(key=lambda service: to_minutes(service.departure))
    return services


def parse_e1_elgoibar(
    forward_pdf: str | Path,
    reverse_pdf: str | Path,
    forward_url: str = "E1 Elgoibar partial",
    reverse_url: str = "E1 Elgoibar partial",
) -> list[Service]:
    return (
        parse_elgoibar_table(forward_pdf, forward_url, WD_FORWARD)
        + parse_elgoibar_table(forward_pdf, forward_url, WE_FORWARD)
        + parse_elgoibar_table(reverse_pdf, reverse_url, WD_REVERSE)
        + parse_elgoibar_table(reverse_pdf, reverse_url, WE_REVERSE)
    )
