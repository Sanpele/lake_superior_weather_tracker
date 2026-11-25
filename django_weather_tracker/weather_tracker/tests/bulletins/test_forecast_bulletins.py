from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import (
    ReportType,
    WindState,
    interpret_bulletin,
)
from weather_tracker.tests.bulletins.helpers import FORECAST_TITLE, REAL_BULLETINS


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
