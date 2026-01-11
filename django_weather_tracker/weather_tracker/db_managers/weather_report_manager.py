import logging

from weather_tracker.models import WeatherReport


class WeatherReportManager:

    def __init__(self):
        self.logger = logging.getLogger()

    def save_list(self, weather_report_list):
        try:
            WeatherReport.objects.bulk_create(weather_report_list)
            return True
        except Exception as e:
            self.logger.exception(e)
            return False
