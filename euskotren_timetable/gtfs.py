"""Load the Euskotren GTFS feed into the normalized timetable model.

The adapter deliberately stops at ``list[Service]``: the workbook, static site,
service ordering and corridor membership continue to consume the same model as
the PDF parsers.
"""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from . import __version__
from .corridors import assign_membership
from .gtfs_stops import canonical_stop
from .model import Service, StopTime
from .service_order import master_sort_key
from .stops import E1_STOPS, E2_STOPS, E3L3_STOPS, E4_STOPS, stop_id

GTFS_SOURCE_URL = "https://opendata.euskadi.eus/transport/moveuskadi/euskotren/gtfs_euskotren.zip"
GTFS_LICENCE = "CC BY 4.0"
GTFS_LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"

ROUTE_LINES = {
    "E1": "E1",
    "E3": "E3-L3",
    "L3": "E3-L3",
    "E4": "E4",
    "T0": "E2-T1",
    "T1": "E2-T1",
}
ROUTE_DIRECTIONS = {
    "E1": ("Pasaia-Matiko", "Matiko-Pasaia"),
    "E3": ("Lezama-Kukullaga", "Kukullaga-Lezama"),
    "L3": ("Matiko-Kukullaga", "Kukullaga-Matiko"),
    "E4": ("Matiko-Bermeo", "Bermeo-Matiko"),
    "T0": ("Hendaia-Lasarte", "Lasarte-Hendaia"),
    "T1": ("Hendaia-Lasarte", "Lasarte-Hendaia"),
}
LINE_STOP_ORDERS = {
    "E1": E1_STOPS,
    "E2-T1": E2_STOPS,
    "E4": E4_STOPS,
    "E3-L3": E3L3_STOPS,
}
LINE_CALENDARS = {
    "E1": {"WD", "SA", "SU", "WE", "SN"},
    "E2-T1": {"WD", "SA", "SU", "WE", "SN"},
    "E4": {"WD", "SU", "WE", "SN"},
    "E3-L3": {"WD", "WE", "FN", "SN"},
}
NIGHT_CALENDARS = {"FN", "SN"}
# The E4 night/transfer tables carry both Amorebieta columns. The day tables
# only carry Geralekua; a trip that serves Geltokia needs the 26-stop order.
E4_TRANSFER_STOPS = E4_STOPS[:13] + ["Amorebieta Geltokia"] + E4_STOPS[13:]
DAY_FIELDS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
REQUIRED_FILES = (
    "routes",
    "trips",
    "stops",
    "stop_times",
    "calendar",
    "calendar_dates",
    "feed_info",
)


@dataclass(frozen=True)
class GtfsFeedMeta:
    source_url: str
    sha256: str
    feed_version: str
    feed_start_date: str
    feed_end_date: str
    fetched_at: str
    publisher: str
    representative_dates: dict[str, str] = field(default_factory=dict)
    licence: str = GTFS_LICENCE
    licence_url: str = GTFS_LICENCE_URL

    def as_manifest(self) -> dict[str, Any]:
        """Return a PDF-manifest-shaped payload for the existing renderers."""
        return {
            "source": "gtfs",
            "source_label": "Euskotren GTFS",
            "licence": self.licence,
            "licence_url": self.licence_url,
            "feed_version": self.feed_version,
            "feed_start_date": self.feed_start_date,
            "feed_end_date": self.feed_end_date,
            "representative_dates": self.representative_dates,
            "files": [
                {
                    "label": "Euskotren GTFS",
                    "url": self.source_url,
                    "path": "",
                    "sha256": self.sha256,
                    "fetched_at": self.fetched_at,
                    "page_count": None,
                    "season": "Winter 2026",
                    "valid_from": self.feed_start_date,
                    "valid_to": self.feed_end_date,
                    "generator_version": __version__,
                }
            ],
        }


def _read_feed(path: Path) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    if path.is_dir():
        for name in REQUIRED_FILES:
            text = (path / f"{name}.txt").read_text(encoding="utf-8-sig")
            tables[name] = list(csv.DictReader(io.StringIO(text)))
        return tables
    with zipfile.ZipFile(path) as archive:
        for name in REQUIRED_FILES:
            text = archive.read(f"{name}.txt").decode("utf-8-sig")
            tables[name] = list(csv.DictReader(io.StringIO(text)))
    return tables


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iso_date(value: str) -> str:
    return datetime.strptime(value, "%Y%m%d").date().isoformat()


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y%m%d").date()


def _normalise_time(value: str) -> str:
    parts = value.split(":")
    if len(parts) < 2:
        raise ValueError(f"invalid GTFS time: {value!r}")
    return f"{int(parts[0])}:{parts[1]}"


def _is_after_midnight(value: str) -> bool:
    return int(value.split(":", 1)[0]) >= 24


def _day_offset(value: str) -> int:
    return 1 if _is_after_midnight(value) else 0


def _active_services(
    day: date,
    calendar: dict[str, dict[str, Any]],
    exceptions: dict[str, list[tuple[str, str]]],
) -> set[str]:
    active = {
        service_id
        for service_id, row in calendar.items()
        if row["start"] <= day <= row["end"] and row["days"][day.weekday()]
    }
    key = day.strftime("%Y%m%d")
    for service_id, exception_type in exceptions.get(key, []):
        if exception_type == "1":
            active.add(service_id)
        elif exception_type == "2":
            active.discard(service_id)
    return active


def _find_normal_date(
    start: date,
    end: date,
    weekdays: set[int],
    calendar: dict[str, dict[str, Any]],
    exceptions: dict[str, list[tuple[str, str]]],
    in_scope_services: set[str],
) -> date:
    current = start
    while current <= end:
        key = current.strftime("%Y%m%d")
        if current.weekday() in weekdays and key not in exceptions:
            if _active_services(current, calendar, exceptions) & in_scope_services:
                return current
        current += timedelta(days=1)
    labels = ",".join(str(day) for day in sorted(weekdays))
    raise ValueError(f"no normal service date for weekdays {labels} in the feed window")


def _in_scope_trips(
    trips: list[dict[str, str]],
    routes: dict[str, dict[str, str]],
    active_services: set[str],
) -> list[dict[str, str]]:
    return [
        trip
        for trip in trips
        if trip["service_id"] in active_services
        and routes.get(trip["route_id"], {}).get("route_short_name") in ROUTE_LINES
    ]


def _has_night_time(stop_times: Iterable[dict[str, str]]) -> bool:
    return any(_is_after_midnight(row["departure_time"]) for row in stop_times)


def _direction_for_trip(
    route: str,
    first_stop: str,
    last_stop: str,
    order: list[str],
) -> str:
    try:
        first_index = order.index(first_stop)
        last_index = order.index(last_stop)
    except ValueError as exc:
        raise ValueError(
            f"{route}: trip stops {first_stop!r} -> {last_stop!r} are outside the line order"
        ) from exc
    if first_index == last_index:
        raise ValueError(f"{route}: trip has the same first and last stop: {first_stop!r}")
    forward, reverse = ROUTE_DIRECTIONS[route]
    return forward if first_index < last_index else reverse


def _service_order(
    route: str,
    direction: str,
    served_stops: set[str],
) -> list[str]:
    line = ROUTE_LINES[route]
    if route == "E4" and "Amorebieta Geltokia" in served_stops:
        order = list(E4_TRANSFER_STOPS)
    else:
        order = list(LINE_STOP_ORDERS[line])
    if direction == ROUTE_DIRECTIONS[route][1]:
        order.reverse()
    unknown = served_stops - set(order)
    if unknown:
        raise ValueError(
            f"{route}: stops outside the canonical line order: {', '.join(sorted(unknown))}"
        )
    return order


def _build_service(
    trip: dict[str, str],
    route: str,
    calendar: str,
    served: list[tuple[str, dict[str, str]]],
    stop_order: list[str],
    source_url: str,
    feed_start: str,
    feed_end: str,
) -> Service:
    served_names = [name for name, _row in served]
    first_stop, first_row = served[0]
    last_stop, last_row = served[-1]
    direction = _direction_for_trip(route, first_stop, last_stop, stop_order)
    order = _service_order(route, direction, set(served_names))

    by_name: dict[str, dict[str, str]] = {}
    for name, row in served:
        if name in by_name:
            raise ValueError(f"{trip['trip_id']}: stop {name!r} occurs more than once")
        by_name[name] = row

    stop_times: list[StopTime] = []
    for index, stop in enumerate(order, 1):
        row = by_name.get(stop)
        if row is None:
            stop_times.append(
                StopTime(
                    stop_id(stop),
                    stop,
                    index,
                    None,
                    "not_served",
                    "not_served",
                    0,
                )
            )
            continue
        value = _normalise_time(row["departure_time"])
        stop_times.append(
            StopTime(
                stop_id(stop),
                stop,
                index,
                value,
                "stop",
                "gtfs",
                _day_offset(row["departure_time"]),
            )
        )

    origin = first_stop
    destination = last_stop
    departure = _normalise_time(first_row["departure_time"])
    arrival = _normalise_time(last_row["arrival_time"])
    pattern = (
        ["night"]
        if calendar in NIGHT_CALENDARS
        else (["through"] if origin == order[0] and destination == order[-1] else ["short-turn"])
    )
    line = ROUTE_LINES[route]
    public_id = f"{line}-{direction.upper()}-{calendar}-{departure.replace(':', '').zfill(4)}"
    return Service(
        service_id=public_id,
        primary_line=line,
        pattern=pattern,
        direction=direction,
        calendar=calendar,
        valid_from=feed_start,
        valid_to=feed_end,
        origin=origin,
        destination=destination,
        departure=departure,
        arrival=arrival,
        source_pdf=source_url,
        frequency_rule_ids=[],
        notes=[],
        appears_in=[],
        stop_times=stop_times,
        gtfs_trip_id=trip["trip_id"],
        gtfs_service_id=trip["service_id"],
    )


def _signature(service: Service) -> tuple[Any, ...]:
    return (
        service.primary_line,
        service.direction,
        service.calendar,
        service.origin,
        service.destination,
        service.departure,
        service.arrival,
        tuple((st.stop_name, st.time, st.disposition) for st in service.stop_times),
    )


def _deduplicate(services: list[Service]) -> list[Service]:
    by_id: dict[str, Service] = {}
    for service in sorted(services, key=lambda item: (item.service_id, item.gtfs_trip_id or "")):
        base_id = service.service_id
        candidate_id = base_id
        suffix = 2
        while candidate_id in by_id:
            existing = by_id[candidate_id]
            if _signature(existing) == _signature(service):
                break
            candidate_id = f"{base_id}-{suffix}"
            suffix += 1
        if candidate_id in by_id:
            continue
        if candidate_id != service.service_id:
            service = replace(service, service_id=candidate_id)
        by_id[candidate_id] = service
    return list(by_id.values())


def load_gtfs_services(
    gtfs_path: str | Path,
    source_url: str = GTFS_SOURCE_URL,
    fetched_at: str | None = None,
) -> tuple[list[Service], GtfsFeedMeta]:
    """Load the in-scope Euskotren GTFS trips as normalized services."""
    path = Path(gtfs_path)
    if not path.exists():
        raise ValueError(f"GTFS feed does not exist: {path}")

    tables = _read_feed(path)
    feed_info = tables["feed_info"][0]
    feed_start_raw = feed_info["feed_start_date"]
    feed_end_raw = feed_info["feed_end_date"]
    feed_start = _iso_date(feed_start_raw)
    feed_end = _iso_date(feed_end_raw)
    start_date = _parse_date(feed_start_raw)
    end_date = _parse_date(feed_end_raw)

    routes = {row["route_id"]: row for row in tables["routes"]}
    stops = {row["stop_id"]: row for row in tables["stops"]}
    trips = tables["trips"]
    stop_times_by_trip: dict[str, list[dict[str, str]]] = {}
    for row in tables["stop_times"]:
        stop_times_by_trip.setdefault(row["trip_id"], []).append(row)
    for rows in stop_times_by_trip.values():
        rows.sort(key=lambda item: int(item["stop_sequence"]))

    in_scope_service_ids = {
        trip["service_id"]
        for trip in trips
        if routes.get(trip["route_id"], {}).get("route_short_name") in ROUTE_LINES
    }

    calendar: dict[str, dict[str, Any]] = {}
    for row in tables["calendar"]:
        calendar[row["service_id"]] = {
            "start": _parse_date(row["start_date"]),
            "end": _parse_date(row["end_date"]),
            "days": tuple(row[field] == "1" for field in DAY_FIELDS),
        }
    exceptions: dict[str, list[tuple[str, str]]] = {}
    for row in tables["calendar_dates"]:
        exceptions.setdefault(row["date"], []).append((row["service_id"], row["exception_type"]))

    mon_thu = _find_normal_date(
        start_date, end_date, {0, 1, 2, 3}, calendar, exceptions, in_scope_service_ids
    )
    friday = _find_normal_date(
        start_date, end_date, {4}, calendar, exceptions, in_scope_service_ids
    )
    saturday = _find_normal_date(
        start_date, end_date, {5}, calendar, exceptions, in_scope_service_ids
    )
    sunday = _find_normal_date(
        start_date, end_date, {6}, calendar, exceptions, in_scope_service_ids
    )
    representative_dates = {
        "WD": mon_thu.isoformat(),
        "WD_FRIDAY": friday.isoformat(),
        "SA": saturday.isoformat(),
        "SU": sunday.isoformat(),
        "WE": f"{saturday.isoformat()}/{sunday.isoformat()}",
        "FN": friday.isoformat(),
        "SN": saturday.isoformat(),
    }

    active_cache = {
        day.isoformat(): _active_services(day, calendar, exceptions)
        for day in {mon_thu, friday, saturday, sunday}
    }
    trips_for = {
        key: _in_scope_trips(trips, routes, active) for key, active in active_cache.items()
    }

    def day_trips(day: date) -> list[dict[str, str]]:
        return [
            trip
            for trip in trips_for[day.isoformat()]
            if not _has_night_time(stop_times_by_trip[trip["trip_id"]])
        ]

    def night_trips(day: date) -> list[dict[str, str]]:
        return [
            trip
            for trip in trips_for[day.isoformat()]
            if _has_night_time(stop_times_by_trip[trip["trip_id"]])
        ]

    trip_sets: dict[str, list[dict[str, str]]] = {
        "WD": day_trips(mon_thu) + day_trips(friday),
        "SA": day_trips(saturday),
        "SU": day_trips(sunday),
        "WE": day_trips(saturday) + day_trips(sunday),
        "FN": night_trips(friday),
        "SN": night_trips(saturday),
    }

    def parent_station(stop_id_value: str) -> str:
        row = stops[stop_id_value]
        return row.get("parent_station") or stop_id_value

    def trip_served(trip: dict[str, str]) -> list[tuple[str, dict[str, str]]]:
        served: list[tuple[str, dict[str, str]]] = []
        for row in stop_times_by_trip[trip["trip_id"]]:
            parent = parent_station(row["stop_id"])
            stop_row = stops[parent]
            served.append((canonical_stop(parent, stop_row["stop_name"]), row))
        return served

    services: list[Service] = []
    for calendar_name, calendar_trips in trip_sets.items():
        seen: set[str] = set()
        for trip in calendar_trips:
            if trip["trip_id"] in seen:
                continue
            route = routes[trip["route_id"]]["route_short_name"]
            line = ROUTE_LINES[route]
            if calendar_name not in LINE_CALENDARS[line]:
                continue
            served = trip_served(trip)
            if len(served) < 2:
                continue
            first_order = (
                E4_TRANSFER_STOPS
                if route == "E4" and any(name == "Amorebieta Geltokia" for name, _ in served)
                else LINE_STOP_ORDERS[line]
            )
            _direction_for_trip(route, served[0][0], served[-1][0], first_order)
            services.append(
                _build_service(
                    trip,
                    route,
                    calendar_name,
                    served,
                    first_order,
                    source_url,
                    feed_start,
                    feed_end,
                )
            )
            seen.add(trip["trip_id"])

    services = _deduplicate(services)
    assign_membership(services)
    services.sort(key=master_sort_key)
    meta = GtfsFeedMeta(
        source_url=source_url,
        sha256=_sha256(path) if path.is_file() else "",
        feed_version=feed_info.get("feed_version", ""),
        feed_start_date=feed_start,
        feed_end_date=feed_end,
        fetched_at=fetched_at or datetime.now(UTC).isoformat(),
        publisher=feed_info.get("feed_publisher_name", "Eusko Trenbideak"),
        representative_dates=representative_dates,
    )
    return services, meta
