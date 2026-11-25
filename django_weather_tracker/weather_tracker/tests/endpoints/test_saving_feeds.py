from weather_tracker.models import WeatherReport
from weather_tracker.tests.testing_mocks import valid_weather_api_response
from weather_tracker.tests.endpoints.helpers import (
    EASTERN_EXTENDED,
    EASTERN_FORECAST,
    LATER_FEED_UPDATED,
    LATER_PUBLISHED,
    WeatherEndpointTestCase,
    feed,
)


class TestSavingFeeds(WeatherEndpointTestCase):

    def test_same_feed_twice__is_only_saved_once(self):
        first = self.ingest(valid_weather_api_response)
        second = self.ingest(valid_weather_api_response)

        self.assertEqual(
            first,
            {"success": True, "info": "Feed saved", "saved": 6, "already_saved": 0},
        )
        self.assertEqual(
            second,
            {"success": True, "info": "Feed saved", "saved": 0, "already_saved": 6},
        )
        self.assertEqual(WeatherReport.objects.count(), 6)

    def test_new_forecast_beside_an_already_saved_bulletin__is_saved(self):
        self.ingest(feed(EASTERN_FORECAST, EASTERN_EXTENDED))

        result = self.ingest(
            feed(
                (
                    "Forecast for Today - Eastern Lake Superior",
                    "Wind north 25 knots.",
                    LATER_PUBLISHED,
                ),
                EASTERN_EXTENDED,
                updated=LATER_FEED_UPDATED,
            )
        )

        self.assertEqual(result["saved"], 1)
        self.assertEqual(result["already_saved"], 1)
        _, eastern = self.daily_conditions()
        self.assertEqual(eastern["wind"]["from_direction"], "north")
        self.assertEqual(eastern["wind"]["speed_knots"], 25.0)

    def test_new_warning_behind_an_already_saved_bulletin__is_saved(self):
        self.ingest(feed(EASTERN_FORECAST))

        result = self.ingest(
            feed(
                EASTERN_FORECAST,
                ("GALE WARNING IN EFFECT, Eastern Lake Superior", "", LATER_PUBLISHED),
                updated=LATER_FEED_UPDATED,
            )
        )

        self.assertEqual(result["saved"], 1)
        self.assertTrue(
            WeatherReport.objects.filter(report_type="GALE_WARNING").exists()
        )

    def test_same_feed_with_warning_twice__is_only_saved_once(self):
        xml = feed(
            ("STRONG WIND WARNING IN EFFECT, Eastern Lake Superior", ""),
            ("Forecast for Today - Eastern Lake Superior", "Wind south 15 knots."),
        )

        self.ingest(xml)
        self.ingest(xml)

        self.assertEqual(WeatherReport.objects.count(), 2)

    def test_watch_and_warning_published_together__are_both_saved(self):
        result = self.ingest(
            feed(
                ("SQUALL WATCH IN EFFECT, Eastern Lake Superior", ""),
                ("SQUALL WARNING IN EFFECT, Eastern Lake Superior", ""),
            )
        )

        self.assertTrue(result["success"])
        self.assertEqual(WeatherReport.objects.count(), 2)
