"""Turns a marine Bulletin's title and text into Conditions.

This module knows Environment Canada's wording. It has no Django or XML
knowledge, so its whole interface is `interpret_bulletin(title, text)`.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum

from weather_tracker.constants import MONTH_NAMES

logger = logging.getLogger(__name__)


class Region(StrEnum):
    EASTERN_LAKE_SUPERIOR = "eastern_lake_superior"
    WESTERN_LAKE_SUPERIOR = "western_lake_superior"
    WHOLE_LAKE = "whole_lake_superior"
    UNDEFINED = "undefined"


class ReportType(StrEnum):
    DETAILED = "detailed"
    WAVES = "waves"
    EXTENDED = "extended"
    STRONG_WIND_WARNING = "STRONG_WIND_WARNING"
    GALE_WARNING = "GALE_WARNING"
    STORM_WARNING = "STORM_WARNING"
    SQUALL_WARNING = "SQUALL_WARNING"
    ICE_PRESSURE_WARNING = "ICE_PRESSURE_WARNING"
    FREEZING_SPRAY_WARNING = "FREEZING_SPRAY_WARNING"
    UNDEFINED = "undefined"


class WarningStatus(StrEnum):
    WATCH = "watch"
    IN_EFFECT = "in_effect"
    ENDED = "ended"


class WindState(StrEnum):
    REPORTED = "reported"
    LIGHT = "light"
    VARIABLE = "variable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OpeningWind:
    state: WindState
    direction: str | None = None
    speed_knots: float | None = None


UNKNOWN_WIND = OpeningWind(WindState.UNKNOWN)


@dataclass(frozen=True)
class Conditions:
    region: Region
    report_type: ReportType
    issued_at: datetime | None
    issued_raw: str
    raw: str


@dataclass(frozen=True)
class ForecastConditions(Conditions):
    wind: OpeningWind
    wind_text: str
    visibility: str | None
    details: tuple[str, ...]


@dataclass(frozen=True)
class WaveConditions(Conditions):
    peak_wave_height_m: float | None
    wave_phrases: tuple[str, ...]


@dataclass(frozen=True)
class ExtendedDay:
    day: str
    wind: str


@dataclass(frozen=True)
class ExtendedConditions(Conditions):
    days: tuple[ExtendedDay, ...]


@dataclass(frozen=True)
class WarningConditions(Conditions):
    warning_status: WarningStatus


_WARNING_KINDS = {
    "STRONG WIND": ReportType.STRONG_WIND_WARNING,
    "GALE": ReportType.GALE_WARNING,
    "STORM": ReportType.STORM_WARNING,
    "SQUALL": ReportType.SQUALL_WARNING,
    "ICE PRESSURE": ReportType.ICE_PRESSURE_WARNING,
    "FREEZING SPRAY": ReportType.FREEZING_SPRAY_WARNING,
}
_WARNING_TITLE_RE = re.compile(
    rf"^\s*({'|'.join(_WARNING_KINDS)})\s+(WARNING|WATCH)\s+(IN EFFECT|ENDED)\b",
    re.IGNORECASE,
)
_ISSUE_ZONES = {
    "EST": timezone(timedelta(hours=-5)),
    "EDT": timezone(timedelta(hours=-4)),
}
_ISSUE_LINE_RE = re.compile(
    r"(?:<br/>\s*)?Issued\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+([A-Z]+)\s+"
    r"(\d{1,2})\s+([a-z]+)\s+(\d{4})\s*$",
    re.IGNORECASE,
)
_COMPASS = r"north(?:east|west)?|south(?:east|west)?|east|west"
_SPEED = r"(\d+(?:\.\d+)?)(?:\s+to\s+(\d+(?:\.\d+)?))?\s+knots\b"
_WIND_START_RE = re.compile(r"\bWind\s+(?!warning\b|watch\b)", re.IGNORECASE)
_LIGHT_RE = re.compile(r"light\b", re.IGNORECASE)
_VARIABLE_RE = re.compile(rf"variable\s+{_SPEED}", re.IGNORECASE)
_REPORTED_RE = re.compile(
    rf"(?:becoming\s+)?({_COMPASS})\s+{_SPEED}",
    re.IGNORECASE,
)
_VISIBILITY_RE = re.compile(r"\bVisibility\s+(.+?)(?:\.\s*|$)", re.IGNORECASE)
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_EXTENDED_DAY_RE = re.compile(r"^(\w+):\s*(.+)$")


def interpret_bulletin(title: str, text: str) -> Conditions:
    title = title or ""
    text = (text or "").strip()
    body, issued_raw, issued_at = _split_issue_line(text)
    report_type, warning_status = _read_title(title)
    common = {
        "region": _read_region(title),
        "report_type": report_type,
        "issued_at": issued_at,
        "issued_raw": issued_raw,
        "raw": text,
    }

    if warning_status is not None:
        return WarningConditions(**common, warning_status=warning_status)
    if common["report_type"] == ReportType.DETAILED:
        return _read_forecast(common, body)
    if common["report_type"] == ReportType.WAVES:
        return _read_waves(common, body)
    if common["report_type"] == ReportType.EXTENDED:
        return _read_extended(common, body)
    return Conditions(**common)


def _split_issue_line(text: str) -> tuple[str, str, datetime | None]:
    match = _ISSUE_LINE_RE.search(text)
    if not match:
        return text, "", None
    body = text[: match.start()].strip()
    issued_raw = match.group(0).replace("<br/>", "").strip()
    return body, issued_raw, _read_issue_time(match)


def _read_issue_time(match: re.Match) -> datetime | None:
    hour, minute, meridiem, zone, day, month, year = match.groups()
    zone_info = _ISSUE_ZONES.get(zone.upper())
    if zone_info is None or month.lower() not in MONTH_NAMES:
        return None

    hour_24 = int(hour) % 12 + (12 if meridiem.upper() == "PM" else 0)
    try:
        return datetime(
            int(year),
            MONTH_NAMES.index(month.lower()) + 1,
            int(day),
            hour_24,
            int(minute),
            tzinfo=zone_info,
        )
    except ValueError:
        return None


def _read_region(title: str) -> Region:
    lowered = title.lower()
    if "western" in lowered:
        return Region.WESTERN_LAKE_SUPERIOR
    if "eastern" in lowered:
        return Region.EASTERN_LAKE_SUPERIOR
    if "lake superior" in lowered:
        return Region.WHOLE_LAKE
    return Region.UNDEFINED


def _read_title(title: str) -> tuple[ReportType, WarningStatus | None]:
    if warning := _WARNING_TITLE_RE.match(title):
        kind, level, state = (group.upper() for group in warning.groups())
        return _WARNING_KINDS[" ".join(kind.split())], _warning_status(level, state)

    lowered = title.lower()
    if "extended forecast" in lowered:
        return ReportType.EXTENDED, None
    if "forecast for" in lowered:
        return ReportType.DETAILED, None
    if "waves for" in lowered:
        return ReportType.WAVES, None
    logger.warning("Unrecognized bulletin title: %s", title)
    return ReportType.UNDEFINED, None


def _warning_status(level: str, state: str) -> WarningStatus:
    if state == "ENDED":
        return WarningStatus.ENDED
    return WarningStatus.WATCH if level == "WATCH" else WarningStatus.IN_EFFECT


def _read_forecast(common: dict, body: str) -> ForecastConditions:
    flattened = body.replace("\n", " ").strip()
    wind = _read_opening_wind(flattened)
    if flattened and wind.state == WindState.UNKNOWN:
        logger.warning("Could not read opening wind from bulletin: %s", common["raw"])

    blocks = [b.strip() for b in re.split(r"\s{2,}", flattened) if b.strip()]
    wind_text = ""
    details = []
    for block in blocks:
        if block.lower().startswith("wind ") and not wind_text:
            wind_text = block
        else:
            details.append(block)

    visibility = _VISIBILITY_RE.search(flattened)
    return ForecastConditions(
        **common,
        wind=wind,
        wind_text=wind_text,
        visibility=visibility.group(1).strip() if visibility else None,
        details=tuple(details),
    )


def _read_waves(common: dict, body: str) -> WaveConditions:
    flattened = body.replace("\n", " ").strip()
    heights = [float(number) for number in _NUMBER_RE.findall(flattened)]
    if flattened and not heights:
        logger.warning("Could not read wave height from bulletin: %s", common["raw"])

    sentences = re.split(r"\.\s+|<br/>\s*", flattened)
    return WaveConditions(
        **common,
        peak_wave_height_m=max(heights) if heights else None,
        wave_phrases=tuple(
            s.strip() for s in sentences if "waves" in s.strip().lower()
        ),
    )


def _read_extended(common: dict, body: str) -> ExtendedConditions:
    days = []
    for segment in re.split(r"<br/>\s*", body.replace("\n", " ")):
        segment = segment.strip()
        if not segment:
            continue
        match = _EXTENDED_DAY_RE.match(segment)
        if match:
            days.append(ExtendedDay(match.group(1), match.group(2).strip()))
        else:
            days.append(ExtendedDay("", segment))
    return ExtendedConditions(**common, days=tuple(days))


def _read_opening_wind(text: str) -> OpeningWind:
    start = _WIND_START_RE.search(text)
    if not start:
        return UNKNOWN_WIND
    phrase = text[start.end() :]

    if _LIGHT_RE.match(phrase):
        return OpeningWind(WindState.LIGHT)
    if variable := _VARIABLE_RE.match(phrase):
        return OpeningWind(
            WindState.VARIABLE,
            speed_knots=_top_of_range(variable.group(1), variable.group(2)),
        )
    if reported := _REPORTED_RE.match(phrase):
        return OpeningWind(
            WindState.REPORTED,
            direction=reported.group(1).lower(),
            speed_knots=_top_of_range(reported.group(2), reported.group(3)),
        )
    return UNKNOWN_WIND


def _top_of_range(low: str, high: str | None) -> float:
    return float(high if high is not None else low)
