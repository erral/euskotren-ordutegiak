"""Parse the Eibar <-> Ermua hourly-repeat tables.

The source prints one hour of the sequence, labels it
``ORDURO ERREPIKATZEN DA ...`` and shows the tail. This parser repeats the
printed head sequence every hour and keeps explicit tail rows.
"""

from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import add_minutes, from_minutes, is_time, to_minutes
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, stop_id

EIBAR_ERMUA_STOPS = E1_FULL_42[16:23]
ERMUA_EIBAR_STOPS = list(reversed(EIBAR_ERMUA_STOPS))


@dataclass(frozen=True)
class EibarConfig:
    stops: list[str]
    origin: str
    direction: str
    slug: str
    calendar: str
    rows: tuple[float, float, float, float, int, float]
    start: str
    end: str
    block: str


WD_FORWARD = EibarConfig(
    stops=EIBAR_ERMUA_STOPS,
    origin="Eibar",
    direction="Pasaia-Matiko",
    slug="EIBAR-ERMUA",
    calendar="WD",
    rows=(1000, 1400, 1040, 1300, 7, 1060),
    start="6:41",
    end="22:11",
    block="E1 Eibar -> Ermua weekday",
)

WE_FORWARD = EibarConfig(
    stops=EIBAR_ERMUA_STOPS,
    origin="Eibar",
    direction="Pasaia-Matiko",
    slug="EIBAR-ERMUA",
    calendar="WE",
    rows=(1000, 1400, 1290, 1470, 7, 1060),
    start="8:00",
    end="22:11",
    block="E1 Eibar -> Ermua weekend",
)

WD_REVERSE = EibarConfig(
    stops=ERMUA_EIBAR_STOPS,
    origin="Ermua",
    direction="Matiko-Pasaia",
    slug="ERMUA-EIBAR",
    calendar="WD",
    rows=(1000, 1400, 1040, 1250, 7, 1060),
    start="6:31",
    end="21:31",
    block="E1 Ermua -> Eibar weekday",
)

WE_REVERSE = EibarConfig(
    stops=ERMUA_EIBAR_STOPS,
    origin="Ermua",
    direction="Matiko-Pasaia",
    slug="ERMUA-EIBAR",
    calendar="WE",
    rows=(1000, 1400, 1290, 1470, 7, 1060),
    start="8:01",
    end="21:42",
    block="E1 Ermua -> Eibar weekend",
)


def _build(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    config: EibarConfig,
    rule_id: str,
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

    notes = [f"Hourly-repeat frequency {rule_id}"]
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
        frequency_rule_ids=[rule_id],
        notes=notes,
        appears_in=[],
        stop_times=stop_times,
    )


def parse_eibar_table(
    pdf: str | Path, source_url: str, config: EibarConfig
) -> tuple[list[Service], FrequencyRule]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    grid_row = next((row for row in rows if len(row) == len(config.stops)), None)
    if grid_row is None:
        raise ValueError(f"{config.block}: no complete rows")
    grid = build_grid(grid_row, config.stops)

    explicit: dict[str, dict[str, str]] = {}
    for row in rows:
        if len(row) != len(config.stops):
            continue
        values = row_to_dict(row, grid)
        departure = values.get(config.origin, "")
        if is_time(departure):
            explicit[departure] = values
    if not explicit:
        raise ValueError(f"{config.block}: no explicit rows")

    start_min = to_minutes(config.start)
    end_min = to_minutes(config.end)
    head = [
        values
        for departure, values in sorted(explicit.items(), key=lambda item: to_minutes(item[0]))
        if start_min <= to_minutes(departure) < start_min + 60
    ]
    if not head:
        raise ValueError(f"{config.block}: hourly head sequence not found")

    rule_id = (
        f"E1-{config.slug}-{config.calendar}-"
        f"{config.start.replace(':', '').zfill(4)}-"
        f"{config.end.replace(':', '').zfill(4)}-60"
    )

    services: list[Service] = []
    generated: set[str] = set()
    cycle_start = start_min
    while cycle_start <= end_min:
        for pattern in head:
            departure = from_minutes(to_minutes(pattern[config.origin]) + cycle_start - start_min)
            if to_minutes(departure) > end_min:
                continue
            offset = to_minutes(departure) - to_minutes(pattern[config.origin])
            record = {
                stop: add_minutes(pattern[stop], offset)
                if is_time(pattern.get(stop))
                else pattern.get(stop, "")
                for stop in config.stops
            }
            source = {stop: "frequency" for stop in config.stops}
            if departure in explicit:
                for stop, value in explicit[departure].items():
                    record[stop] = value
                    source[stop] = "full"
            services.append(_build(departure, record, source, source_url, config, rule_id))
            generated.add(departure)
        cycle_start += 60

    for departure, values in explicit.items():
        if departure in generated:
            continue
        record = {stop: values.get(stop, "") for stop in config.stops}
        source = {stop: ("full" if stop in values else "not_served") for stop in config.stops}
        service = _build(departure, record, source, source_url, config, rule_id)
        service.frequency_rule_ids = []
        service.notes = [
            note for note in service.notes if not note.startswith("Hourly-repeat")
        ]
        service.notes.append("Explicit service outside the hourly range")
        services.append(service)

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=(
            f"{config.start} > {config.end} ORDURO ERREPIKATZEN DA "
            "ORDUTEGI-SEGIDA / LA SECUENCIA HORARIA SE REPITE CADA HORA"
        ),
        source_pdf=source_url,
        page=1,
        block=config.block,
        origin=config.origin,
        start=config.start,
        end=config.end,
        interval_minutes=60,
        calendar=config.calendar,
        expanded_service_ids=[
            f"E1-{config.slug}-{config.calendar}-{departure.replace(':', '').zfill(4)}"
            for departure in sorted(generated, key=to_minutes)
        ],
    )
    return services, rule


def parse_e1_eibar(
    forward_pdf: str | Path,
    reverse_pdf: str | Path,
    forward_url: str = "E1 Eibar partial",
    reverse_url: str = "E1 Eibar partial",
) -> tuple[list[Service], list[FrequencyRule]]:
    services: list[Service] = []
    rules: list[FrequencyRule] = []
    for pdf, url, config in (
        (forward_pdf, forward_url, WD_FORWARD),
        (forward_pdf, forward_url, WE_FORWARD),
        (reverse_pdf, reverse_url, WD_REVERSE),
        (reverse_pdf, reverse_url, WE_REVERSE),
    ):
        block_services, rule = parse_eibar_table(pdf, url, config)
        services.extend(block_services)
        rules.append(rule)
    return services, rules
