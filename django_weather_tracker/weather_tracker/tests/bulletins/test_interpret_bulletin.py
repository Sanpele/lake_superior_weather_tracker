import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import (
    Region,
    ReportType,
    WarningStatus,
    WindState,
    interpret_bulletin,
)

REAL_BULLETINS = json.loads(
    (Path(__file__).parent / "real_bulletins.json").read_text(encoding="utf-8")
)
FORECAST_TITLE = "Forecast for Today Tonight and Tuesday. - Eastern Lake Superior"
WAVES_TITLE = "Waves for Today Tonight and Tuesday. - Eastern Lake Superior"


class TestForecastBulletins(SimpleTestCase):

    def test_real_forecasts__give_opening_wind_and_visibility(self):
        for bulletin in REAL_BULLETINS["forecasts"]:
            with self.subTest(text=bulletin["text"][:70]):
                conditions = interpret_bulletin(bulletin["title"], bulletin["text"])
                expected = bulletin["expected"]

                self.assertEqual(conditions.report_type, ReportType.DETAILED)
                self.assertEqual(conditions.wind.state, expected["wind_state"])
                self.assertEqual(conditions.wind.direction, expected["wind_direction"])
                self.assertEqual(
                    conditions.wind.speed_knots, expected["wind_speed_knots"]
                )
                if expected["visibility"]:
                    self.assertEqual(conditions.visibility, expected["visibility"])

    def test_opening_wind__agreed_readings(self):
        cases = [
            ("Wind northwest 15 to 20 knots.", WindState.REPORTED, "northwest", 20),
            (
                "Wind light increasing to southwest 15 knots.",
                WindState.LIGHT,
                None,
                None,
            ),
            ("Wind becoming east 15 knots.", WindState.REPORTED, "east", 15),
            (
                "Wind south 15 knots diminishing to northwest 10.",
                WindState.REPORTED,
                "south",
                15,
            ),
            (
                "Wind northwest 20 knots except northeast 10 over eastern sections.",
                WindState.REPORTED,
                "northwest",
                20,
            ),
        ]
        for text, state, direction, speed in cases:
            with self.subTest(text=text):
                wind = interpret_bulletin(FORECAST_TITLE, text).wind
                self.assertEqual(
                    (wind.state, wind.direction, wind.speed_knots),
                    (state, direction, speed),
                )

    def test_unreadable_wind__is_unknown_and_logged(self):
        text = "Wind doing something unexpected."

        with self.assertLogs(
            "weather_tracker.bulletin_interpretation", level="WARNING"
        ) as logs:
            wind = interpret_bulletin(FORECAST_TITLE, text).wind

        self.assertEqual(wind.state, WindState.UNKNOWN)
        self.assertIsNone(wind.direction)
        self.assertIsNone(wind.speed_knots)
        self.assertIn(text, logs.output[0])


class TestWaveBulletins(SimpleTestCase):

    def test_real_wave_bulletins__give_peak_height(self):
        for bulletin in REAL_BULLETINS["waves"]:
            with self.subTest(text=bulletin["text"][:70]):
                conditions = interpret_bulletin(bulletin["title"], bulletin["text"])

                self.assertEqual(conditions.report_type, ReportType.WAVES)
                self.assertEqual(
                    conditions.peak_wave_height_m, bulletin["expected_peak_m"]
                )

    def test_peak_height__includes_except_clause(self):
        conditions = interpret_bulletin(
            WAVES_TITLE, "Waves 1 to 1.5 metres except 2 over northern sections."
        )

        self.assertEqual(conditions.peak_wave_height_m, 2)

    def test_edt_issue_line__is_not_read_as_a_wave_height(self):
        conditions = interpret_bulletin(
            WAVES_TITLE,
            "Waves 1 metre.<br/>Issued 10:30  AM EDT 16 June 2026",
        )

        self.assertEqual(conditions.peak_wave_height_m, 1)

    def test_wave_text_without_a_height__is_unknown_and_logged(self):
        text = "Waves unavailable."

        with self.assertLogs(
            "weather_tracker.bulletin_interpretation", level="WARNING"
        ) as logs:
            conditions = interpret_bulletin(WAVES_TITLE, text)

        self.assertIsNone(conditions.peak_wave_height_m)
        self.assertIn(text, logs.output[0])


class TestExtendedBulletins(SimpleTestCase):

    def test_real_extended_bulletins__keep_each_day(self):
        for bulletin in REAL_BULLETINS["extended"]:
            with self.subTest(text=bulletin["text"][:70]):
                conditions = interpret_bulletin(bulletin["title"], bulletin["text"])

                self.assertEqual(conditions.report_type, ReportType.EXTENDED)
                self.assertEqual(
                    [day.day for day in conditions.days], bulletin["expected_days"]
                )
                self.assertTrue(all(day.wind for day in conditions.days))


class TestIssueTimes(SimpleTestCase):

    def test_est_and_edt__are_timezone_aware(self):
        cases = [
            (
                "Issued 10:30  AM EST 16 February 2026",
                -5,
                datetime(2026, 2, 16, 10, 30),
            ),
            ("Issued 6:30  PM EDT 13 June 2026", -4, datetime(2026, 6, 13, 18, 30)),
            ("Issued 12:00  PM EDT 13 June 2026", -4, datetime(2026, 6, 13, 12, 0)),
            ("Issued 12:15  AM EST 16 February 2026", -5, datetime(2026, 2, 16, 0, 15)),
        ]
        for line, offset, local in cases:
            with self.subTest(line=line):
                conditions = interpret_bulletin(
                    WAVES_TITLE, f"Waves 1 metre.<br/>{line}"
                )

                self.assertEqual(
                    conditions.issued_at,
                    local.replace(tzinfo=timezone(timedelta(hours=offset))),
                )

    def test_other_zone__has_unknown_issue_time_and_line_is_removed(self):
        conditions = interpret_bulletin(
            WAVES_TITLE, "Waves 1 metre.<br/>Issued 10:30  AM CDT 16 June 2026"
        )

        self.assertIsNone(conditions.issued_at)
        self.assertEqual(conditions.peak_wave_height_m, 1)


class TestMarineWarnings(SimpleTestCase):

    def test_observed_titles__give_kind_status_and_area(self):
        east, west, lake = (
            Region.EASTERN_LAKE_SUPERIOR,
            Region.WESTERN_LAKE_SUPERIOR,
            Region.WHOLE_LAKE,
        )
        strong, gale, storm = (
            ReportType.STRONG_WIND_WARNING,
            ReportType.GALE_WARNING,
            ReportType.STORM_WARNING,
        )
        squall, ice, spray = (
            ReportType.SQUALL_WARNING,
            ReportType.ICE_PRESSURE_WARNING,
            ReportType.FREEZING_SPRAY_WARNING,
        )
        active, ended, watch = (
            WarningStatus.IN_EFFECT,
            WarningStatus.ENDED,
            WarningStatus.WATCH,
        )
        cases = [
            (
                "STRONG WIND WARNING IN EFFECT, Eastern Lake Superior",
                strong,
                active,
                east,
            ),
            (
                "STRONG WIND WARNING IN EFFECT, Western Lake Superior",
                strong,
                active,
                west,
            ),
            ("STRONG WIND WARNING IN EFFECT, Lake Superior", strong, active, lake),
            ("STRONG WIND WARNING ENDED , Eastern Lake Superior", strong, ended, east),
            ("STRONG WIND WARNING ENDED , Western Lake Superior", strong, ended, west),
            ("STRONG WIND WARNING ENDED , Lake Superior", strong, ended, lake),
            (
                "ICE PRESSURE WARNING IN EFFECT, Eastern Lake Superior",
                ice,
                active,
                east,
            ),
            (
                "ICE PRESSURE WARNING IN EFFECT, Western Lake Superior",
                ice,
                active,
                west,
            ),
            ("ICE PRESSURE WARNING ENDED , Eastern Lake Superior", ice, ended, east),
            ("ICE PRESSURE WARNING ENDED , Western Lake Superior", ice, ended, west),
            ("SQUALL WATCH IN EFFECT, Eastern Lake Superior", squall, watch, east),
            ("SQUALL WATCH IN EFFECT, Western Lake Superior", squall, watch, west),
            ("SQUALL WARNING IN EFFECT, Eastern Lake Superior", squall, active, east),
            ("SQUALL WARNING IN EFFECT, Western Lake Superior", squall, active, west),
            ("SQUALL WARNING ENDED , Western Lake Superior", squall, ended, west),
            ("STORM WARNING IN EFFECT, Eastern Lake Superior", storm, active, east),
            ("GALE WARNING IN EFFECT, Eastern Lake Superior", gale, active, east),
            ("GALE WARNING IN EFFECT, Western Lake Superior", gale, active, west),
            ("GALE WARNING ENDED , Eastern Lake Superior", gale, ended, east),
            ("GALE WARNING ENDED , Western Lake Superior", gale, ended, west),
            (
                "FREEZING SPRAY WARNING IN EFFECT, Eastern Lake Superior",
                spray,
                active,
                east,
            ),
            (
                "FREEZING SPRAY WARNING IN EFFECT, Western Lake Superior",
                spray,
                active,
                west,
            ),
            (
                "FREEZING SPRAY WARNING ENDED , Eastern Lake Superior",
                spray,
                ended,
                east,
            ),
            (
                "FREEZING SPRAY WARNING ENDED , Western Lake Superior",
                spray,
                ended,
                west,
            ),
        ]
        for title, report_type, status, region in cases:
            with self.subTest(title=title):
                conditions = interpret_bulletin(
                    title, "Issued 6:30  PM EDT 13 June 2026"
                )

                self.assertEqual(conditions.report_type, report_type)
                self.assertEqual(conditions.warning_status, status)
                self.assertEqual(conditions.region, region)
                self.assertIsNotNone(conditions.issued_at)

    def test_issue_line_only_warning__logs_nothing(self):
        with self.assertNoLogs("weather_tracker.bulletin_interpretation"):
            interpret_bulletin(
                "GALE WARNING IN EFFECT, Eastern Lake Superior",
                "Issued 6:30  PM EST 12 January 2026",
            )

    def test_unrecognized_title__stays_undefined_and_is_logged(self):
        title = "WATERSPOUT WARNING IN EFFECT, Eastern Lake Superior"

        with self.assertLogs(
            "weather_tracker.bulletin_interpretation", level="WARNING"
        ) as logs:
            conditions = interpret_bulletin(title, "Issued 6:30  PM EDT 13 June 2026")

        self.assertEqual(conditions.report_type, ReportType.UNDEFINED)
        self.assertIn(title, logs.output[0])
