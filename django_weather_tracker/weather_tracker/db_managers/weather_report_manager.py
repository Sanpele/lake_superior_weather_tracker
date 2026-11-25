import logging

from django.db import transaction
from django.db.models import Max

from weather_tracker.models import WeatherReport


class WeatherReportManager:

    def __init__(self):
        self.logger = logging.getLogger()

    def save_list(self, weather_report_list: list[WeatherReport]) -> tuple[int, int]:
        """Save each Bulletin not already stored. Returns (saved, already_saved)."""
        saved = 0
        with transaction.atomic():
            for report in weather_report_list:
                already_stored = WeatherReport.objects.filter(
                    region=report.region,
                    report_type=report.report_type,
                    warning_status=report.warning_status,
                    published_time=report.published_time,
                ).update(last_seen_at=report.last_seen_at)
                if not already_stored:
                    report.save()
                    saved += 1
        return saved, len(weather_report_list) - saved

    def get_latest_weather_reports(self):
        """The Bulletins in the newest feed we read."""
        newest_feed = WeatherReport.objects.aggregate(newest=Max("last_seen_at"))[
            "newest"
        ]
        return list(WeatherReport.objects.filter(last_seen_at=newest_feed))
