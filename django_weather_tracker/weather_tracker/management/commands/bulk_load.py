import os

import xmltodict
from django.core.management.base import BaseCommand

from weather_tracker.db_managers.weather_report_manager import WeatherReportManager
from weather_tracker.parsers.marine_xml_historical_parser import (
    MarineXmlHistoricalParser,
)


class Command(BaseCommand):
    help = "Bulk load data from specific file path"

    def add_arguments(self, parser):
        parser.add_argument("parent_dir", type=str)

    def handle(self, *args, **options):
        file_path = options["parent_dir"]

        filenames_to_process = []
        count = 0
        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(file_path):
            path = root.split(os.sep)
            print((len(path) - 1) * "---", os.path.basename(root))

            for file in files:
                filename_exploded = file.split(".")

                if len(filename_exploded) != 3:
                    continue

                date, filename, extension = filename_exploded

                if extension != "xml":
                    continue

                language = filename[-2:]

                if language != "en":
                    continue

                count += 1
                print(len(path) * "---", file)
                filenames_to_process.append(f"{root}/{file}")

        print("TOTAL NUMBER OF FILES: ", count)

        weather_report_list = []
        for file_path in filenames_to_process:
            with open(file_path, "r") as f:
                weather_xml = f.read()
                weather_dict = xmltodict.parse(weather_xml)
                weather_report_day_list = MarineXmlHistoricalParser().parse(
                    weather_dict
                )
                weather_report_list.extend(weather_report_day_list)

        WeatherReportManager().save_list(weather_report_list)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully saved {len(weather_report_list)} weather reports"
            )
        )
