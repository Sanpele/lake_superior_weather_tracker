from dataclasses import dataclass


@dataclass
class WeatherReport:
    title: str
    date: str
    wind_info: str
    wave_info: str
    weather_and_visibility: str
    extended_forecast: str = None
    synopsis: str = None
