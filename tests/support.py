from euskotren_timetable.model import Service, StopTime
from euskotren_timetable.parse_e1 import add_minutes


def make_service(
    service_id: str,
    calendar: str,
    line: str,
    direction: str,
    departure: str,
    stops: tuple[str, ...] = ("Origin",),
) -> Service:
    stop_times = [
        StopTime(
            f"S{index:03d}",
            stop,
            index,
            add_minutes(departure, index - 1),
            "stop",
            "test",
        )
        for index, stop in enumerate(stops, 1)
    ]
    return Service(
        service_id=service_id,
        primary_line=line,
        pattern=["test"],
        direction=direction,
        calendar=calendar,
        valid_from="2026-11-21",
        valid_to=None,
        origin=stops[0],
        destination=stops[-1],
        departure=departure,
        arrival=stop_times[-1].time,
        source_pdf="test",
        frequency_rule_ids=[],
        notes=[],
        appears_in=[],
        stop_times=stop_times,
    )
