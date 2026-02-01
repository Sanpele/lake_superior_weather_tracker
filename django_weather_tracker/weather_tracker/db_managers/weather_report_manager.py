import logging

from django.db.models import Max

from weather_tracker.models import WeatherReport, ReportType


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

    def get_latest_weather_reports(self):
        try:
            latest_published_time = WeatherReport.objects.aggregate(
                max_pt=Max("published_time")
            )["max_pt"]
            weather_reports = WeatherReport.objects.filter(
                published_time=latest_published_time
            )
            return weather_reports
        except Exception as e:
            self.logger.exception(e)
            return False

    def build_daily_report_summary(self, weather_reports):

        if len(weather_reports) != 3:
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
