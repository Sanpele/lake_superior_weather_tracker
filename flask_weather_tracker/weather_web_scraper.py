import copy
import re
from datetime import datetime
from typing import Dict

from bs4 import BeautifulSoup

from flask_weather_tracker.constants import INTERNAL_FAILURE_MSG, WORD_REDUCTION_MAP
from flask_weather_tracker.utils import (
    call_function_on_str_fields_of_class,
    get_request,
)
from flask_weather_tracker.weather_report_dataclass import WeatherReport


class GovWeatherScraper:
    urls: Dict[str, str] = {
        "Weastern Lake Superior": "https://weather.gc.ca/marine/forecast_e.html?mapID=09&siteID=08507",
        "Eastern Lake Superior": "https://weather.gc.ca/marine/forecast_e.html?mapID=09&siteID=08503",
    }

    def get(self):
        try:
            html_documents = {}
            for key, url in self.urls.items():
                html_documents[key] = get_request(url)

            weather_report: Dict[str, WeatherReport] = self.get_info(html_documents)
            single_string_report = self.format_info(weather_report)
            simple_response = {"compressed_summary_string": single_string_report}

            return simple_response
        except Exception as e:
            print(e)
            raise Exception(INTERNAL_FAILURE_MSG)

    @staticmethod
    def get_info(html_doc_dict: Dict[str, str]) -> Dict[str, WeatherReport]:
        weather_reports = {}

        for page_title, page_content in html_doc_dict.items():
            soup = BeautifulSoup(page_content, "html.parser")

            extended_str = soup.find(id="forecast-content").text
            extended_str = re.sub("[^A-Za-z0-9 &.]+", "", extended_str)
            broken_into_category = extended_str.split("Issued")

            same_date = True
            initial_date = ""
            for idx, category in enumerate(broken_into_category):
                current_year = str(datetime.now().year)
                broken_into_category[idx] = category.split(current_year)

                # check if date diff
                if idx > 1 and same_date:
                    if category[0] != initial_date:
                        same_date = False
                initial_date = category[0]

            title = page_title
            date = f"{broken_into_category[1][0]} for {broken_into_category[1][1].split('.', 1)[0]}"
            wind_info = broken_into_category[2][1].replace("Waves", "").split(".", 1)[1]
            wave_info = (
                broken_into_category[3][1]
                .replace("Weather & Visibility", "")
                .split(".", 1)[1]
            )
            weather_and_visibility = (
                broken_into_category[4][1]
                .replace("Extended Forecast", "")
                .split(".", 1)[1]
            )

            weather_report = WeatherReport(
                title=title,
                date=date,
                wind_info=wind_info,
                wave_info=wave_info,
                weather_and_visibility=weather_and_visibility,
            )

            weather_reports[page_title] = weather_report

        return weather_reports

    def format_info(
        self, weather_report: Dict[str, WeatherReport], include_date_title=False
    ) -> str:
        final_output = ""

        for key, report in weather_report.items():
            # only returning eastern data right now. Parameterize later
            if key != "Eastern Lake Superior":
                continue

            report = self.reduce_chars(report)

            first_sentence_format = ""
            if include_date_title and len(report.title) > 0 and len(report.date) > 0:
                first_sentence_format += f"{report.title}:{report.date}:"

            first_sentence_format += (
                f"{report.wind_info}:{report.wave_info}:{report.weather_and_visibility}"
            )

            first_sentence_format = first_sentence_format.replace(" ", "")
            first_sentence_format = first_sentence_format[:159]

            final_output += first_sentence_format

        return final_output

    @staticmethod
    def reduce_chars(weather_report: WeatherReport) -> WeatherReport:
        weather_report.title = ""
        weather_report.date = ""
        weather_report.wave_info = weather_report.wave_info.split(".Exten")[0]
        weather_report.wind_info = (
            weather_report.wind_info.split(".")[0]
            + "."
            + weather_report.wind_info.split(".")[1]
        )
        weather_report.weather_and_visibility = (
            weather_report.weather_and_visibility.split(".")[0]
        )

        # lower all words in each field before maping to get all cases
        call_function_on_str_fields_of_class(weather_report, lambda x: x.lower())

        # Replace long words
        for key, value in WORD_REDUCTION_MAP.items():
            pattern = re.compile(key, re.IGNORECASE)
            weather_report.wave_info = pattern.sub(value, weather_report.wave_info)
            weather_report.wind_info = pattern.sub(value, weather_report.wind_info)
            weather_report.weather_and_visibility = pattern.sub(
                value, weather_report.weather_and_visibility
            )

        # Capitalize all words in each field
        call_function_on_str_fields_of_class(weather_report, lambda x: x.title())

        return weather_report

    @staticmethod
    def reduce_chars_v2(original_string: str) -> str:
        copied_string = copy.deepcopy(original_string)
        word_list = copied_string.split()

        processed_list = []
        for word in word_list:
            word = word.lower()
            if word in WORD_REDUCTION_MAP:
                word = WORD_REDUCTION_MAP[word]
            word = word.title()
            processed_list.append(word)

        return "".join(processed_list)
