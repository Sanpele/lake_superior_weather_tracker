from weather_tracker.tests.endpoints.helpers import (
    EASTERN_FORECAST,
    LATER_FEED_UPDATED,
    LATER_PUBLISHED,
    WeatherEndpointTestCase,
    feed,
)


class TestCurrentBulletins(WeatherEndpointTestCase):

    def test_unchanged_bulletins__stay_current_in_a_newer_feed(self):
        waves = ("Waves for Today - Eastern Lake Superior", "Waves 1 metre.")
        self.ingest(feed(EASTERN_FORECAST, waves))

        self.ingest(
            feed(
                EASTERN_FORECAST,
                (
                    "Waves for Today - Eastern Lake Superior",
                    "Waves 2 metres.",
                    LATER_PUBLISHED,
                ),
                updated=LATER_FEED_UPDATED,
            )
        )

        response = self.client.get("/weather-report/").json()
        _, eastern = response["daily_conditions"]
        self.assertEqual(response["updated_at"], LATER_FEED_UPDATED)
        self.assertEqual(eastern["wind"]["from_direction"], "south")
        self.assertEqual(eastern["peak_wave_height_m"], 2.0)

    def test_bulletin_missing_from_the_newest_feed__is_no_longer_current(self):
        western_forecast = (
            "Forecast for Today - Western Lake Superior",
            "Wind west 10 knots.",
        )
        self.ingest(feed(EASTERN_FORECAST, western_forecast))

        self.ingest(feed(western_forecast, updated=LATER_FEED_UPDATED))

        western, eastern = self.daily_conditions()
        self.assertEqual(western["wind"]["from_direction"], "west")
        self.assertEqual(eastern["wind"]["state"], "unknown")
