from dataclasses import dataclass
from datetime import datetime


@dataclass
class SpecificEntry:
    title: str
    published: datetime
    category: str
    summary: str


@dataclass
class WeatherReport:
    title: str
    date: datetime

    eastern_forcast: SpecificEntry
    eastern_waves: SpecificEntry
    eastern_extended: SpecificEntry

    western_forecast: SpecificEntry
    western_waves: SpecificEntry
    western_extended: SpecificEntry
