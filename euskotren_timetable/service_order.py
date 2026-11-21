"""Canonical service row order for the workbook.

The rules are specified in ``.scratch/service-sorting/spec.md``. Keep the rank
tables and keys here so the Master and corridor renderers share one contract.
"""

from .model import Service
from .parse_e1 import to_minutes

CALENDAR_ORDER = ("WD", "SA", "SU", "WE", "FN", "SN")
LINE_ORDER = ("E1", "E2-T1", "E4", "E3-L3")
DIRECTION_ORDER = {
    "E1": ("Pasaia-Matiko", "Matiko-Pasaia"),
    "E2-T1": ("Hendaia-Lasarte", "Lasarte-Hendaia"),
    "E4": ("Matiko-Bermeo", "Bermeo-Matiko"),
    # E3-L3 carries both the E3 branch and the L3 local. The E3 branch
    # directions keep the published sheet order; the L3 local directions follow.
    "E3-L3": (
        "Lezama-Kukullaga",
        "Kukullaga-Lezama",
        "Matiko-Kukullaga",
        "Kukullaga-Matiko",
    ),
}

CALENDAR_RANK = {calendar: index for index, calendar in enumerate(CALENDAR_ORDER)}
LINE_RANK = {line: index for index, line in enumerate(LINE_ORDER)}
DIRECTION_RANK = {
    (line, direction): index
    for line, directions in DIRECTION_ORDER.items()
    for index, direction in enumerate(directions)
}


def _rank(table: dict, key, label: str) -> int:
    try:
        return table[key]
    except KeyError as exc:
        raise ValueError(f"unknown {label}: {key!r}") from exc


def _calendar_rank(service: Service) -> int:
    return _rank(CALENDAR_RANK, service.calendar, "calendar")


def _line_rank(service: Service) -> int:
    return _rank(LINE_RANK, service.primary_line, "line")


def _direction_rank(service: Service) -> int:
    return _rank(
        DIRECTION_RANK,
        (service.primary_line, service.direction),
        f"direction for {service.primary_line!r}",
    )


def _departure_minutes(service: Service) -> int:
    if not service.departure:
        raise ValueError(f"service {service.service_id!r} has no departure")
    return to_minutes(service.departure)


def master_sort_key(service: Service) -> tuple[int, int, int, int, str]:
    return (
        _calendar_rank(service),
        _departure_minutes(service),
        _line_rank(service),
        _direction_rank(service),
        service.service_id,
    )


def corridor_sort_key(
    service: Service, own_line: str
) -> tuple[int, int, int, int, str]:
    return (
        _departure_minutes(service),
        0 if service.primary_line == own_line else 1,
        _line_rank(service),
        _direction_rank(service),
        service.service_id,
    )
