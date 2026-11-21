"""Corridor definitions and cross-line membership for both directions."""

from dataclasses import dataclass

from .model import Service
from .stops import E1_STOPS, E2_STOPS, E3L3_STOPS, E4_STOPS


@dataclass(frozen=True)
class Corridor:
    line: str
    sheet: str
    direction: str
    stops: tuple[str, ...]
    direction_sign: int


CORRIDORS = (
    Corridor("E1", "E1 Pasaia-Matiko", "Pasaia-Matiko", tuple(E1_STOPS), -1),
    Corridor("E1", "E1 Matiko-Pasaia", "Matiko-Pasaia", tuple(reversed(E1_STOPS)), +1),
    Corridor("E2-T1", "E2-T1 Hendaia-Lasarte", "Hendaia-Lasarte", tuple(E2_STOPS), -1),
    Corridor("E2-T1", "E2-T1 Lasarte-Hendaia", "Lasarte-Hendaia", tuple(reversed(E2_STOPS)), +1),
    Corridor("E4", "E4 Matiko-Bermeo", "Matiko-Bermeo", tuple(E4_STOPS), +1),
    Corridor("E4", "E4 Bermeo-Matiko", "Bermeo-Matiko", tuple(reversed(E4_STOPS)), -1),
    Corridor("E3-L3", "E3-L3 Lezama-Kukullaga", "Lezama-Kukullaga", tuple(E3L3_STOPS), +1),
    Corridor(
        "E3-L3", "E3-L3 Kukullaga-Lezama", "Kukullaga-Lezama", tuple(reversed(E3L3_STOPS)), -1
    ),
)

DIRECTION_SIGNS = {
    "Pasaia-Matiko": -1,
    "Matiko-Pasaia": +1,
    "Hendaia-Lasarte": -1,
    "Lasarte-Hendaia": +1,
    "Matiko-Bermeo": +1,
    "Bermeo-Matiko": -1,
    "Lezama-Kukullaga": +1,
    "Kukullaga-Lezama": -1,
    "Matiko-Kukullaga": +1,
    "Kukullaga-Matiko": -1,
}


def appears_in(service: Service, corridor: Corridor) -> bool:
    """A service appears where it calls at two or more corridor stops."""
    if DIRECTION_SIGNS.get(service.direction) != corridor.direction_sign:
        return False
    served = {
        stop_time.stop_name
        for stop_time in service.stop_times
        if stop_time.disposition in ("stop", "unpublished")
    }
    return sum(1 for stop in corridor.stops if stop in served) >= 2


def assign_membership(services: list[Service]) -> None:
    for service in services:
        service.appears_in = [
            corridor.sheet for corridor in CORRIDORS if appears_in(service, corridor)
        ]


def services_for_corridor(services: list[Service], corridor: Corridor) -> list[Service]:
    return [service for service in services if corridor.sheet in service.appears_in]
