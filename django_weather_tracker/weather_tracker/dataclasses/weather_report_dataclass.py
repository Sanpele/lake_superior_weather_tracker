from dataclasses import dataclass
from datetime import datetime
from typing import Optional

"""
schema to return from API
"""


@dataclass
class SpecificEntry:
    title: str
    published: datetime
    category: str
    summary: str


@dataclass
class WeatherReport:
    cardinal_direction: str  # east or west
    title: str
    date: datetime

    forcast: SpecificEntry
    waves: SpecificEntry
    extended: SpecificEntry

    wind_direction: Optional[str] = None
    wind_speed: Optional[str] = None
    wave_height: Optional[str] = None
