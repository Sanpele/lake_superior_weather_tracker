import logging

from django.db.models import Max

from weather_tracker.models import WeatherReport, ReportType


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
        try:
            latest_updated_time = WeatherReport.objects.aggregate(
                max_pt=Max("updated_time")
            )["max_pt"]
            weather_reports = WeatherReport.objects.filter(
                updated_time=latest_updated_time
            )
            return weather_reports
        except Exception as e:
            self.logger.exception(e)
            return False

    def build_daily_report_summary(self, weather_reports):
        if len(weather_reports) != 3:
            self.logger.info(
                f"something went wrong, not expected number of weather reports {weather_reports}"
            )
            return None

        region = weather_reports[0].region

        wave_report = None
        detailed_report = None
        extended_report = None
        for report in weather_reports:
            if report.report_type == ReportType.DETAILED:
                detailed_report = report
            elif report.report_type == ReportType.EXTENDED:
                extended_report = report
            elif report.report_type == ReportType.WAVES:
                wave_report = report

        return {
            "region": region,
            "wind_direction": detailed_report.wind_direction,
            "wind_speed": detailed_report.wind_speed_knots,
            "wave_height": wave_report.max_wave_height_m,
            "visibility": extended_report.visibility_text,
        }
