from datetime import datetime

from weather_tracker.bulletin_interpretation import (
    Conditions,
    ForecastConditions,
    WarningConditions,
    WaveConditions,
    WindState,
    interpret_bulletin,
)
from weather_tracker.models import Category, WeatherReport
from weather_tracker.parsers.generic_parser import GenericParser


def stored_fields(conditions: Conditions) -> dict:
    """The WeatherReport fields that come from a Bulletin's Conditions."""
    fields = {
        "region": conditions.region.value,
        "report_type": conditions.report_type.value,
        "warning_status": "",
        "wind_state": WindState.UNKNOWN.value,
        "wind_direction": None,
        "wind_speed_knots": None,
        "max_wave_height_m": None,
        "visibility_text": None,
    }
    if isinstance(conditions, ForecastConditions):
        fields["wind_state"] = conditions.wind.state.value
        fields["wind_direction"] = conditions.wind.direction
        fields["wind_speed_knots"] = conditions.wind.speed_knots
        fields["visibility_text"] = conditions.visibility
    elif isinstance(conditions, WaveConditions):
        fields["max_wave_height_m"] = conditions.peak_wave_height_m
    elif isinstance(conditions, WarningConditions):
        fields["warning_status"] = conditions.warning_status.value
    return fields


class MarineXmlAPIParser(GenericParser):

    def parse(self, raw_data) -> list[WeatherReport]:

        report_list = self.parse_webpage_and_create_reports(raw_data)

        return report_list

    def parse_webpage_and_create_reports(self, raw_report_dict):
        main_data = raw_report_dict.get("feed")
        entry_list = main_data.get("entry", [])

        report_list = [
            self.parse_weather_entry(
                main_data,
                entry,
            )
            for entry in entry_list
        ]

        return report_list

    def parse_weather_entry(self, main_data, entry_dict):
        if not main_data or not entry_dict:
            return None

        updated_str = main_data.get("updated")
        updated_time = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
        title = entry_dict.get("title", "")
        summary = entry_dict.get("summary", {}).get("#text", "")

        return WeatherReport(
            title=title,
            date=updated_time.date(),
            published_time=entry_dict.get("published"),
            updated_time=updated_time,
            category=Category.MARINE,
            summary=summary,
            link=entry_dict.get("link", {}).get("@href"),  # webpage link,
            weather_canada_id=entry_dict.get("id"),
            **stored_fields(interpret_bulletin(title, summary)),
        )
