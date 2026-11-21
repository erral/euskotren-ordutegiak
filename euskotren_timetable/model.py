"""Normalized records shared by the parser, validator and workbook renderer."""

from dataclasses import dataclass, field


@dataclass
class StopTime:
    stop_id: str
    stop_name: str
    sequence: int
    time: str | None
    disposition: str  # stop | pass | not_served | unpublished
    source: str
    day_offset: int = 0


@dataclass
class Service:
    service_id: str
    primary_line: str
    pattern: list[str]
    direction: str
    calendar: str
    valid_from: str
    valid_to: str | None
    origin: str
    destination: str
    departure: str
    arrival: str
    source_pdf: str
    frequency_rule_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    appears_in: list[str] = field(default_factory=list)
    stop_times: list[StopTime] = field(default_factory=list)


@dataclass
class FrequencyRule:
    rule_id: str
    source_text: str
    source_pdf: str
    page: int
    block: str
    origin: str
    start: str
    end: str
    interval_minutes: float
    calendar: str
    expanded_service_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class ManifestEntry:
    url: str
    path: str
    sha256: str
    fetched_at: str
    page_count: int
    season: str
    valid_from: str
    valid_to: str | None
    generator_version: str
