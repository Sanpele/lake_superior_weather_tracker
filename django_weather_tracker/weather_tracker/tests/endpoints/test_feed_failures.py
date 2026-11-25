from unittest.mock import Mock, patch

import requests

from weather_tracker.models import WeatherReport
from weather_tracker.tests.endpoints.helpers import (
    EASTERN_FORECAST,
    GET_REQUEST,
    LATER_FEED_UPDATED,
    WeatherEndpointTestCase,
    feed,
)


class TestFeedFailures(WeatherEndpointTestCase):

    def setUp(self):
        self.ingest(feed(EASTERN_FORECAST))

    def assert_failed_and_nothing_changed(self, response):
        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json(),
            {"success": False, "info": "Could not read the marine feed"},
        )
        self.assertEqual(WeatherReport.objects.count(), 1)
        _, eastern = self.daily_conditions()
        self.assertEqual(eastern["wind"]["from_direction"], "south")

    def test_single_entry_feed__is_saved(self):
        result = self.ingest(
            feed(("Waves for Today - Eastern Lake Superior", "Waves 1 metre."))
        )

        self.assertEqual(result["saved"], 1)

    def test_feed_request_timing_out__fails_after_20_seconds(self):
        with patch(
            "weather_tracker.utils.requests.get", side_effect=requests.Timeout
        ) as get:
            response = self.client.post("/weather/")

        self.assertEqual(get.call_args.kwargs["timeout"], 20)
        self.assert_failed_and_nothing_changed(response)

    def test_feed_request_refused__fails(self):
        refused = Mock(status_code=503, text="Service unavailable")
        with patch("weather_tracker.utils.requests.get", return_value=refused):
            response = self.client.post("/weather/")

        self.assert_failed_and_nothing_changed(response)

    def test_unreadable_feed__fails(self):
        with patch(GET_REQUEST, return_value="<html>maintenance</html"):
            response = self.client.post("/weather/")

        self.assert_failed_and_nothing_changed(response)

    def test_feed_with_no_bulletins__fails(self):
        with patch(GET_REQUEST, return_value=feed(updated=LATER_FEED_UPDATED)):
            response = self.client.post("/weather/")

        self.assert_failed_and_nothing_changed(response)
