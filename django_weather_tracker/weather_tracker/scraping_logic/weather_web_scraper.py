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

        updated_str = main_data.get("updated")
        updated_time = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
        date = updated_time.date()

        published_time = entry_dict.get("published")
        weather_canada_id = entry_dict.get("id")
        link = entry_dict.get("link", {}).get("@href")  # webpage link,
        title = entry_dict.get("title", "")
        summary = entry_dict.get("summary", {}).get("#text", "")

        report_type = self.extract_report_type(title)
        report_region = self.extract_report_region(title)

        weather_report = WeatherReport(
            region=report_region,
            report_type=report_type,
            title=title,
            date=date,
            published_time=published_time,
            updated_time=updated_time,
            category=Category.MARINE,
            summary=summary,
            link=link,
            weather_canada_id=weather_canada_id,
        )

        return weather_report

    @staticmethod
    def extract_report_type(title: str) -> ReportType:
        title = title.lower()

        if "extended forecast" in title:
            report_type = ReportType.EXTENDED
        elif "forecast for" in title:
            report_type = ReportType.DETAILED
        elif "waves for" in title:
            report_type = ReportType.WAVES
        else:
            report_type = ReportType.UNDEFINED

        return report_type

    @staticmethod
    def extract_report_region(title: str) -> Region:
        title = title.lower()

        if "western" in title:
            region = Region.WESTERN_LAKE_SUPERIOR
        elif "eastern" in title:
            region = Region.EASTERN_LAKE_SUPERIOR
        else:
            region = Region.UNDEFINED

        return region
