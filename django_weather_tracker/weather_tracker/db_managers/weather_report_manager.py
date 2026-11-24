import logging

from django.db.models import Max

from weather_tracker.models import WeatherReport


class WeatherReportManager:

    def __init__(self):
        self.logger = logging.getLogger()

    def save_list(self, weather_report_list: list[WeatherReport]):
        try:
            have_we_already_saved_today = WeatherReport.objects.filter(
                published_time=weather_report_list[0].published_time
            ).exists()

            if have_we_already_saved_today:
                return False, "we already saved today bud :)"

            WeatherReport.objects.bulk_create(weather_report_list)
            return True, "saved successfully"
        except Exception as e:
            self.logger.exception(e)
            return False, "something went wrong"

    def get_latest_weather_reports(self):
        latest_updated_time = WeatherReport.objects.aggregate(
            max_pt=Max("updated_time")
        )["max_pt"]
        return list(WeatherReport.objects.filter(updated_time=latest_updated_time))
