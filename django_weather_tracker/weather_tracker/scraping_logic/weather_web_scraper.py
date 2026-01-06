from datetime import datetime
from typing import Tuple

import xmltodict

from weather_tracker.constants import INTERNAL_FAILURE_MSG
from weather_tracker.models import Region, ReportType, Category, WeatherReport
from weather_tracker.utils import (
    get_request,
)

XML_URL = "https://weather.gc.ca/rss/marine/08500_e.xml"


class GovWeatherScraper:

    def get(self):
        try:
            weather_xml = get_request(XML_URL)
            weather_dict = xmltodict.parse(weather_xml)
            weather_report_list = self.parse_webpage_and_create_reports(weather_dict)
            return weather_report_list
        except Exception as e:
            print(e)
            raise Exception(INTERNAL_FAILURE_MSG)

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

    def get_info(self, raw_report_dict) -> Tuple[WeatherReport, WeatherReport]:
        main_data = raw_report_dict.get("feed")
        title = main_data.get("title")
        date_str = main_data.get("updated")  # re-visit
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        entry_list = main_data.get("entry")

        (
            eastern_forcast,
            eastern_waves,
            eastern_extended,
            western_forecast,
            western_waves,
            western_extended,
        ) = (
            self.process_single_weather_entry(entry_list, 0),
            self.process_single_weather_entry(entry_list, 1),
            self.process_single_weather_entry(entry_list, 2),
            self.process_single_weather_entry(entry_list, 3),
            self.process_single_weather_entry(entry_list, 4),
            self.process_single_weather_entry(entry_list, 5),
        )

        eastern_weather_report = WeatherReport(
            cardinal_direction="east",
            title=title,
            date=date,
            forcast=eastern_forcast,
            waves=eastern_waves,
            extended=eastern_extended,
        )

        western_weather_report = WeatherReport(
            cardinal_direction="west",
            title=title,
            date=date,
            forcast=western_forecast,
            waves=western_waves,
            extended=western_extended,
        )

        return eastern_weather_report, western_weather_report

    def parse_weather_entry(self, main_data, entry_dict):
        if not main_data or not entry_dict:
            return None

        report_type = self.extract_report_type(entry_dict)
        report_region = self.extract_report_region(entry_dict)

        weather_report = WeatherReport(
            region=report_region,
            report_type=report_type,
            title=main_data.get("title"),
            date="",
            published_time=entry_dict.get("published"),
            updated_time="today",
            category=Category.MARINE,
            summary="placeholder :)",
            link="https://www.weather.gc.ca/marine/forecast_e.html?mapID=09&siteID=08507#forecast",
            weather_canada_id="abc123",
        )

        return weather_report

    def extract_report_type(self, weather_entry: dict) -> ReportType:
        pass

    def extract_report_region(self, weather_entry: dict) -> Region:
        pass
