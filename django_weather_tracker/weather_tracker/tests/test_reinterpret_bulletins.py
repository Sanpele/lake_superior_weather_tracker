from datetime import datetime, timezone
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from weather_tracker.models import WeatherReport

PUBLISHED = datetime(2026, 6, 16, 14, 30, tzinfo=timezone.utc)
ISSUE_LINE = "<br/>Issued 10:30  AM EDT 16 June 2026"


def stored_report(title, text, **fields):
    defaults = {
        "region": "undefined",
        "report_type": "undefined",
        "title": title,
        "date": PUBLISHED.date(),
        "published_time": PUBLISHED,
        "updated_time": PUBLISHED,
        "category": "marine",
        "summary": f"{text}{ISSUE_LINE}",
        "link": "https://www.weather.gc.ca/marine",
        "weather_canada_id": title,
    }
    return WeatherReport.objects.create(**{**defaults, **fields})


def repair(*args):
    output = StringIO()
    call_command("reinterpret_bulletins", *args, stdout=output)
    return output.getvalue()


class TestReinterpretBulletins(TestCase):

    def bad_wave_report(self):
        return stored_report(
            "Waves for Today - Eastern Lake Superior",
            "Waves 1 metre.",
            region="eastern_lake_superior",
            report_type="waves",
            max_wave_height_m=2026.0,
        )

    def test_default_run__reports_changes_without_saving(self):
        report = self.bad_wave_report()

        output = repair()

        report.refresh_from_db()
        self.assertEqual(report.max_wave_height_m, 2026.0)
        self.assertIn("Dry run", output)
        self.assertIn("max_wave_height_m: 1", output)

    def test_apply__repairs_waves_wind_and_warnings(self):
        waves = self.bad_wave_report()
        forecast = stored_report(
            "Forecast for Today - Eastern Lake Superior",
            "Wind light becoming east 15 knots.",
            region="eastern_lake_superior",
            report_type="detailed",
            wind_direction="east",
            wind_speed_knots=15.0,
        )
        warning = stored_report("STRONG WIND WARNING IN EFFECT, Lake Superior", "")

        repair("--apply")

        for report in (waves, forecast, warning):
            report.refresh_from_db()
        self.assertEqual(waves.max_wave_height_m, 1.0)
        self.assertEqual(forecast.wind_state, "light")
        self.assertIsNone(forecast.wind_direction)
        self.assertIsNone(forecast.wind_speed_knots)
        self.assertEqual(warning.report_type, "STRONG_WIND_WARNING")
        self.assertEqual(warning.warning_status, "in_effect")
        self.assertEqual(warning.region, "whole_lake_superior")

    def test_second_apply__changes_nothing(self):
        self.bad_wave_report()
        repair("--apply")

        output = repair("--apply")

        self.assertIn("Rows to change: 0", output)

    def conflicting_reports(self):
        title = "STRONG WIND WARNING IN EFFECT, Eastern Lake Superior"
        old = stored_report(title, "", region="eastern_lake_superior")
        stored_report(
            title,
            "",
            region="eastern_lake_superior",
            report_type="STRONG_WIND_WARNING",
            warning_status="in_effect",
        )
        return old

    def test_conflict__is_listed_in_dry_run(self):
        self.conflicting_reports()

        output = repair()

        self.assertIn("Conflicts: 1", output)

    def test_conflict__aborts_apply_and_changes_nothing(self):
        old = self.conflicting_reports()
        waves = self.bad_wave_report()

        with self.assertRaises(CommandError):
            repair("--apply")

        old.refresh_from_db()
        waves.refresh_from_db()
        self.assertEqual(old.report_type, "undefined")
        self.assertEqual(waves.max_wave_height_m, 2026.0)
        self.assertEqual(WeatherReport.objects.count(), 3)
