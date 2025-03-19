from datetime import datetime

import xmltodict

from flask_weather_tracker.constants import INTERNAL_FAILURE_MSG
from flask_weather_tracker.utils import (
    get_request,
)
from flask_weather_tracker.weather_report_dataclass import WeatherReport, SpecificEntry

XML_URL = "https://weather.gc.ca/rss/marine/08500_e.xml"


class GovWeatherScraper:

    def get(self):
        try:
            weather_xml = get_request(XML_URL)
            weather_dict = xmltodict.parse(weather_xml)
            weather_report = self.get_info(weather_dict)
            return weather_report
        except Exception as e:
            print(e)
            raise Exception(INTERNAL_FAILURE_MSG)

    def get_info(self, raw_report_dict) -> WeatherReport:
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

        weather_report = WeatherReport(
            title=title,
            date=date,
            eastern_forcast=eastern_forcast,
            eastern_waves=eastern_waves,
            eastern_extended=eastern_extended,
            western_forecast=western_forecast,
            western_waves=western_waves,
            western_extended=western_extended,
        )

        return weather_report

    @staticmethod
    def process_single_weather_entry(weather_entry, index):
        if not weather_entry or len(weather_entry) != 6:
            return None

        specific_entry_dict = weather_entry[index]

        specific_entry = SpecificEntry(
            title=specific_entry_dict.get("title"),
            published=specific_entry_dict.get("published"),
            category=specific_entry_dict.get("category", {}).get("@term"),
            summary=specific_entry_dict.get("summary", {}).get("#text"),
        )

        return specific_entry
