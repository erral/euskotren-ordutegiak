"""Parse the E3-L3 night blocks.

The L3 local has Friday-night and Saturday-night tables in both directions.
The E3 Lezama branch has Saturday-night tables only. After-midnight times are
stored on the extended clock (24:xx, 25:xx, ...).
"""

from dataclasses import dataclass
from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import is_time, to_minutes
from .parse_e2 import parse_frequency_note
from .parse_night import extend_times, from_minutes_extended
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E3L3_STOPS, stop_id

L3_STOPS = E3L3_STOPS[9:]
L3_REVERSE_STOPS = list(reversed(L3_STOPS))
E3_REVERSE_STOPS = list(reversed(E3L3_STOPS))


@dataclass(frozen=True)
class L3NightTable:
    stops: list[str]
    origin: str
    direction: str
    slug: str
    calendar: str
    rows: tuple[float, float, float, float, int, float]
    note: tuple[float, float, float, float, float, float]
    block: str


L3_FN_FORWARD = L3NightTable(
    stops=L3_STOPS,
    origin="Matiko-Bilbao",
    direction="Matiko-Kukullaga",
    slug="MATIKO-KUKULLAGA",
    calendar="FN",
    rows=(80, 330, 940, 1170, 7, 120),
    note=(1125, 1140, 80, 300, 80, 320),
    block="L3 Matiko -> Kukullaga Friday night",
)

L3_SN_FORWARD = L3NightTable(
    stops=L3_STOPS,
    origin="Matiko-Bilbao",
    direction="Matiko-Kukullaga",
    slug="MATIKO-KUKULLAGA",
    calendar="SN",
    rows=(408, 660, 940, 1170, 7, 448),
    note=(1100, 1115, 410, 640, 410, 660),
    block="L3 Matiko -> Kukullaga Saturday night",
)

L3_FN_REVERSE = L3NightTable(
    stops=L3_REVERSE_STOPS,
    origin="Kukullaga-Etxebarri",
    direction="Kukullaga-Matiko",
    slug="KUKULLAGA-MATIKO",
    calendar="FN",
    rows=(780, 1035, 950, 1170, 7, 820),
    note=(1117, 1130, 780, 1010, 780, 1035),
    block="L3 Kukullaga -> Matiko Friday night",
)

L3_SN_REVERSE = L3NightTable(
    stops=L3_REVERSE_STOPS,
    origin="Kukullaga-Etxebarri",
    direction="Kukullaga-Matiko",
    slug="KUKULLAGA-MATIKO",
    calendar="SN",
    rows=(1105, 1360, 950, 1170, 7, 1145),
    note=(1105, 1118, 1100, 1340, 1100, 1360),
    block="L3 Kukullaga -> Matiko Saturday night",
)

E3_FORWARD = L3NightTable(
    stops=E3L3_STOPS,
    origin="Lezama",
    direction="Lezama-Kukullaga",
    slug="LEZAMA-KUKULLAGA",
    calendar="SN",
    rows=(80, 660, 1745, 1870, 16, 120),
    note=(),
    block="E3 Lezama -> Kukullaga Saturday night",
)

E3_REVERSE = L3NightTable(
    stops=E3_REVERSE_STOPS,
    origin="Kukullaga-Etxebarri",
    direction="Kukullaga-Lezama",
    slug="KUKULLAGA-LEZAMA",
    calendar="SN",
    rows=(780, 1360, 1745, 1870, 16, 820),
    note=(),
    block="E3 Kukullaga -> Lezama Saturday night",
)


def _extended_start(value: str) -> int:
    minutes = to_minutes(value)
    return minutes + (1440 if minutes < 12 * 60 else 0)


def _extended_end(start: str, end: str) -> int:
    return _extended_start(start) + (to_minutes(end) - to_minutes(start)) % 1440


def _service_id(config: L3NightTable, departure: str) -> str:
    return (
        f"E3-L3-{config.slug}-{config.calendar}-"
        f"{departure.replace(':', '').zfill(4)}"
    )


def _build_service(
    record: dict[str, str],
    offsets: dict[str, int],
    source_url: str,
    config: L3NightTable,
    rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in config.stops if is_time(record.get(stop))]
    origin, departure = timed[0]
    destination, arrival = timed[-1]

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(config.stops, 1):
        if stop in record and is_time(record[stop]):
            stop_times.append(
                StopTime(
                    stop_id(stop),
                    stop,
                    sequence,
                    record[stop],
                    "stop",
                    "night",
                    offsets.get(stop, 0),
                )
            )
        else:
            stop_times.append(
                StopTime(stop_id(stop), stop, sequence, None, "not_served", "not_served", 0)
            )

    if config.calendar == "FN":
        note = "Friday night / holiday eve"
    else:
        note = "Saturday night (Noches del sábado al domingo)"

    return Service(
        service_id=_service_id(config, departure),
        primary_line="E3-L3",
        pattern=["night"],
        direction=config.direction,
        calendar=config.calendar,
        valid_from="2026-11-21",
        valid_to=None,
        origin=origin,
        destination=destination,
        departure=departure,
        arrival=arrival,
        source_pdf=source_url,
        frequency_rule_ids=[rule_id] if rule_id else [],
        notes=[note],
        appears_in=[],
        stop_times=stop_times,
    )


def _explicit_extended(record: dict[str, str], stops: list[str]) -> tuple[dict[str, str], dict[str, int]]:
    timed = [(stop, record[stop]) for stop in stops if is_time(record.get(stop))]
    extended = extend_times(timed)
    return (
        {stop: time for stop, _offset, time in extended},
        {stop: offset for stop, offset, _time in extended},
    )


def parse_l3_night_table(
    pdf: str | Path, source_url: str, config: L3NightTable
) -> tuple[list[Service], FrequencyRule | None]:
    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, *config.rows)
    complete = [row for row in rows if len(row) == len(config.stops)]
    if not complete:
        raise ValueError(f"{config.block}: no complete rows")

    grid = build_grid(complete[0], config.stops)
    explicit: dict[str, tuple[dict[str, str], dict[str, int]]] = {}
    for row in complete:
        record = row_to_dict(row, grid)
        if not is_time(record.get(config.origin)):
            continue
        times, offsets = _explicit_extended(record, config.stops)
        departure = times[config.origin]
        explicit[departure] = (times, offsets)

    if not config.note:
        services: list[Service] = []
        for times, offsets in explicit.values():
            services.append(_build_service(times, offsets, source_url, config, None))
        services.sort(key=lambda service: to_minutes(service.departure))
        return services, None

    start, end, interval = parse_frequency_note(words, *config.note)
    rule_id = (
        f"E3-L3-{config.slug}-{config.calendar}-"
        f"{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-"
        f"{int(interval)}"
    )

    start_extended = _extended_start(start)
    template_key = from_minutes_extended(start_extended)
    if template_key not in explicit:
        template_key = next(
            departure for departure in sorted(explicit, key=to_minutes)
            if to_minutes(departure) >= start_extended
        )
    template_times, _template_offsets = explicit[template_key]
    template_start = to_minutes(template_key)

    departures = [
        from_minutes_extended(value)
        for value in range(start_extended, _extended_end(start, end) + 1, int(interval))
    ]

    services = []
    generated: list[str] = []
    for departure in departures:
        offset = to_minutes(departure) - template_start
        times: dict[str, str] = {}
        offsets: dict[str, int] = {}
        for stop in config.stops:
            value = template_times.get(stop)
            if not is_time(value):
                continue
            extended = to_minutes(value) + offset
            times[stop] = from_minutes_extended(extended)
            offsets[stop] = extended // 1440
        if departure in explicit:
            times, offsets = explicit[departure]
        services.append(_build_service(times, offsets, source_url, config, rule_id))
        generated.append(departure)

    for departure, (times, offsets) in explicit.items():
        if departure in departures:
            continue
        services.append(_build_service(times, offsets, source_url, config, None))

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=(
            f"{start} > {end} MAIZTASUNA FRECUENCIA {int(interval)} min"
        ),
        source_pdf=source_url,
        page=1,
        block=config.block,
        origin=config.origin,
        start=start,
        end=end,
        interval_minutes=interval,
        calendar=config.calendar,
        expanded_service_ids=[
            _service_id(config, departure) for departure in generated
        ],
    )
    return services, rule


def parse_l3_night(
    pdf: str | Path, source_url: str = "E3-L3 night"
) -> tuple[list[Service], list[FrequencyRule]]:
    services: list[Service] = []
    rules: list[FrequencyRule] = []
    for config in (
        L3_FN_FORWARD,
        L3_SN_FORWARD,
        L3_FN_REVERSE,
        L3_SN_REVERSE,
    ):
        block_services, rule = parse_l3_night_table(pdf, source_url, config)
        services.extend(block_services)
        if rule:
            rules.append(rule)
    return services, rules


def parse_e3_night(
    pdf: str | Path, source_url: str = "E3 night"
) -> list[Service]:
    services: list[Service] = []
    for config in (E3_FORWARD, E3_REVERSE):
        block_services, _rule = parse_l3_night_table(pdf, source_url, config)
        services.extend(block_services)
    services.sort(key=lambda service: to_minutes(service.departure))
    return services
