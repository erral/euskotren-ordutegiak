"""Parse the E1 Matiko -> Pasaia weekday full-line table.

The reverse poster has several partial tables and a night block. This slice
parses the full-line weekday table and the Altzola footnote; the reverse
partial and night tables are deferred.
"""

from pathlib import Path

from .model import FrequencyRule, Service, StopTime
from .parse_e1 import (
    ALTZOLA,
    add_minutes,
    from_minutes,
    is_time,
    parse_altzola_footnote,
    parse_frequency_note,
    to_minutes,
)
from .pdf import build_grid, cluster_rows, row_to_dict, words_from_pdf
from .stops import E1_FULL_42, E1_STOPS, E1_TOP0_MISSING, stop_id

E1_REVERSE_STOPS = list(reversed(E1_STOPS))
E1_REVERSE_42 = list(reversed(E1_FULL_42))
MENDARO = "Mendaro"
TOLETXEGAIN = "Toletxegain (Elgoibar)"
PASAIA = "Pasaia"


def _generate_hourly(start: str, end: str, interval: int) -> list[str]:
    current = to_minutes(start)
    last = to_minutes(end)
    out = []
    while current <= last:
        out.append(from_minutes(current))
        current += interval
    return out


def _build_service(
    departure: str,
    record: dict[str, str],
    source: dict[str, str],
    source_url: str,
    rule_id: str | None,
) -> Service:
    timed = [(stop, record[stop]) for stop in E1_REVERSE_STOPS if is_time(record.get(stop))]
    origin, origin_time = timed[0]
    destination, arrival = timed[-1]
    origin_is_full = origin == E1_REVERSE_STOPS[0]
    pattern = ["through"] if origin_is_full and destination == PASAIA else ["short-turn"]
    notes: list[str] = []
    if rule_id:
        notes.append(f"Hourly frequency {rule_id}")
    else:
        notes.append("Explicit service outside the frequency range")
    if not origin_is_full:
        notes.append(f"Partial from {origin}")
    if destination != PASAIA:
        notes.append(f"Short-turn to {destination}")
    if is_time(record.get(ALTZOLA)):
        notes.append("Altzola conditional stop")

    stop_times: list[StopTime] = []
    for sequence, stop in enumerate(E1_REVERSE_STOPS, 1):
        value = record.get(stop, "")
        if is_time(value):
            disposition, time = "stop", value
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
        service_id=f"E1-MATIKO-PASAIA-WD-{departure.replace(':', '').zfill(4)}",
        primary_line="E1",
        pattern=pattern,
        direction="Matiko-Pasaia",
        calendar="WD",
        valid_from="2026-11-21",
        valid_to=None,
        origin=origin,
        destination=destination,
        departure=origin_time,
        arrival=arrival,
        source_pdf=source_url,
        frequency_rule_ids=[rule_id] if rule_id else [],
        notes=notes,
        appears_in=[],
        stop_times=stop_times,
    )


def parse_e1_reverse(
    pdf: str | Path, source_url: str = "E1 Matiko - Pasaia_4.pdf"
) -> tuple[list[Service], FrequencyRule]:
    from .parse_e1_partial import (
        REVERSE_WEEKDAY,
        expand_partial_block,
        fill_service_from_partial,
    )

    words = words_from_pdf(pdf, page=1)
    rows = cluster_rows(words, 50, 1420, 430, 560, 10, 1400)
    if not rows:
        raise ValueError("could not find the E1 reverse full-line table")

    complete = next((row for row in rows if len(row) == len(E1_REVERSE_42)), None)
    if complete is None:
        raise ValueError("could not find a complete E1 reverse full-line row")
    grid = build_grid(complete, E1_REVERSE_42)
    records = [row_to_dict(row, grid) for row in rows]
    explicit = {
        values["Matiko-Bilbao"]: values
        for values in records
        if is_time(values.get("Matiko-Bilbao"))
    }
    partial_rows = [
        values
        for values in records
        if not is_time(values.get("Matiko-Bilbao"))
        and sum(1 for stop in E1_REVERSE_42 if is_time(values.get(stop))) >= 2
    ]

    start, end, interval = parse_frequency_note(words)
    template_departure = start if start in explicit else min(explicit, key=to_minutes)
    template = explicit[template_departure]
    footnote_times = parse_altzola_footnote(pdf)
    rule_id = (
        f"E1-WD-{start.replace(':', '').zfill(4)}-{end.replace(':', '').zfill(4)}-{int(interval)}"
    )

    services: list[Service] = []
    for departure in _generate_hourly(start, end, int(interval)):
        offset = to_minutes(departure) - to_minutes(start)
        record_42 = {
            stop: add_minutes(template[stop], offset)
            if is_time(template.get(stop))
            else template.get(stop, "")
            for stop in E1_REVERSE_42
        }
        source_42 = {stop: "frequency" for stop in E1_REVERSE_42}
        if departure in explicit:
            for stop, value in explicit[departure].items():
                record_42[stop] = value
                source_42[stop] = "full"

        record = {}
        source = {}
        for stop in E1_REVERSE_STOPS:
            if stop in record_42:
                record[stop] = record_42[stop]
                source[stop] = source_42[stop]
            else:
                record[stop] = "?"
                source[stop] = "unpublished"
        services.append(_build_service(departure, record, source, source_url, rule_id))

    for values in partial_rows:
        timed = [(stop, values[stop]) for stop in E1_REVERSE_42 if is_time(values.get(stop))]
        if len(timed) < 2:
            continue
        departure = timed[0][1]
        record = {}
        source = {}
        for stop in E1_REVERSE_STOPS:
            if stop in values:
                record[stop] = values[stop]
                source[stop] = "full"
            elif stop in E1_TOP0_MISSING:
                record[stop] = "?"
                source[stop] = "unpublished"
            else:
                record[stop] = ""
                source[stop] = "not_served"
        services.append(_build_service(departure, record, source, source_url, None))

    for service in services:
        altzola = next(st for st in service.stop_times if st.stop_name == ALTZOLA)
        if altzola.disposition != "pass":
            continue
        mendaro = next(st for st in service.stop_times if st.stop_name == MENDARO)
        toletxegain = next(st for st in service.stop_times if st.stop_name == TOLETXEGAIN)
        if not (is_time(mendaro.time) and is_time(toletxegain.time)):
            continue
        for value in footnote_times:
            if to_minutes(mendaro.time) < to_minutes(value) < to_minutes(toletxegain.time):
                altzola.time = value
                altzola.disposition = "stop"
                altzola.source = "footnote"
                service.notes.append("Altzola conditional stop")
                break

    partial = expand_partial_block(words, REVERSE_WEEKDAY)
    for service in services:
        fill_service_from_partial(
            service,
            partial,
            "Zumaia",
            E1_TOP0_MISSING,
            "Topo times from Zumaia-Pasaia partial table",
        )

    services.sort(key=lambda service: to_minutes(service.departure))
    rule = FrequencyRule(
        rule_id=rule_id,
        source_text=f"{start} > {end} MAIZTASUNA FRECUENCIA {int(interval) // 60} h",
        source_pdf=source_url,
        page=1,
        block="E1 Matiko -> Pasaia weekday",
        origin="Matiko-Bilbao",
        start=start,
        end=end,
        interval_minutes=interval,
        calendar="WD",
        expanded_service_ids=[
            service.service_id for service in services if rule_id in service.frequency_rule_ids
        ],
    )
    return services, rule
