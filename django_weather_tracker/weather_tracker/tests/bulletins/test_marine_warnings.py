from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import (
    Region,
    ReportType,
    WarningStatus,
    interpret_bulletin,
)


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
