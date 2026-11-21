"""Parse the E2/T1 full-line combined weekend tables.

The E2 shuttle has separate Saturday and Sunday/holiday blocks; this slice
parses the full-line combined weekend only and defers the SA/SU shuttle.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .parse_e2 import generate_fixed, parse_frequency_note
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E2_STOPS, stop_id

E2_REVERSE_STOPS = list(reversed(E2_STOPS))


@dataclass(frozen=True)
class E2WeekendConfig:
    stops: list[str]
    origin: str
    direction: str
    slug: str
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str


FORWARD = E2WeekendConfig(
    stops=E2_STOPS,
    origin="Hendaia",
    direction="Hendaia-Lasarte",
    slug="HENDAIA-LASARTE",
    rows=(50, 850, 850, 950, 20, 120),
    note=(915, 935, 400, 420, 300, 600),
    block="E2-T1 Hendaia -> Lasarte-Oria weekend",
)

REVERSE = E2WeekendConfig(
    stops=E2_REVERSE_STOPS,
    origin="Lasarte-Oria",
    direction="Lasarte-Hendaia",
    slug="LASARTE-HENDAIA",
    rows=(50, 850, 850, 950, 20, 120),
    note=(885, 905, 380, 410, 300, 600),
    block="E2-T1 Lasarte-Oria -> Hendaia weekend",
)


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: E2WeekendConfig,
    frequency_rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    notes = ["Weekend (Saturday, Sunday + holiday)"]
    notes.append(
        f"30-minute frequency {frequency_rule_id}"
        if frequency_rule_id
        else "Explicit service outside the frequency range"
    )

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
        service_id=f"E2-T1-{config.slug}-WE-{departure.replace(':', '').zfill(4)}",
        primary_line="E2-T1",
        pattern=["full"],
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


def parse_e2_weekend_direction(
    pdf: str | Path, source_url: str, config: E2WeekendConfig
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    if not rows:
        raise ValueError("E2 weekend rows not found")

    grid = build_grid(next(row for row in rows if len(row) == len(config.stops)), config.stops)
    explicit = {}
    for row in rows:
        values = row_to_dict(row, grid)
        if is_time(values.get(config.origin)):
            explicit[values[config.origin]] = values
    if not explicit:
        raise ValueError("E2 weekend full-line row not found")

    start, end, interval = parse_frequency_note(words, *config.note)
    template_departure = next(
        departure
        for departure in sorted(explicit, key=to_minutes)
        if to_minutes(departure) >= to_minutes(start)
    )
    template = explicit[template_departure]
    generated = generate_fixed(template_departure, end, interval)
    rule_id = (
        f"E2-T1-WE-{start.replace(':', '').zfill(4)}-"
        f"{end.replace(':', '').zfill(4)}-{int(interval)}"
    )

    services: list[Service] = []
    for departure in generated:
        offset = to_minutes(departure) - to_minutes(template_departure)
        record = {
            stop: add_minutes(template[stop], offset)
            if is_time(template.get(stop))
            else template.get(stop, "")
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
        source_text=f"{start} > {end} MAIZTASUNA FRECUENCIA {int(interval)} min",
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


def parse_e2_weekend(
    pdf: str | Path, source_url: str = "T1 Hendaia - Lasarte/Oria weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e2_weekend_direction(pdf, source_url, FORWARD)


def parse_e2_weekend_reverse(
    pdf: str | Path, source_url: str = "T1 Lasarte/Oria - Hendaia weekend"
) -> tuple[list[Service], FrequencyRule]:
    return parse_e2_weekend_direction(pdf, source_url, REVERSE)
