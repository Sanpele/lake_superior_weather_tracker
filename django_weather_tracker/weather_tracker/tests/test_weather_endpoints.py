from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase

from weather_tracker.models import WeatherReport
from weather_tracker.tests.testing_mocks import valid_weather_api_response

GET_REQUEST = "weather_tracker.scraping_logic.weather_web_scraper.get_request"
ISSUE_LINE = "&#60;br/>Issued 10:30  AM EDT 16 June 2026"


def feed(*entries):
    body = "".join(
        f"""<entry>
        <title>{title}</title>
        <link type="text/html" href="https://www.weather.gc.ca/marine"/>
        <published>2026-06-16T14:30:00Z</published>
        <summary type="html">{text}{ISSUE_LINE}</summary>
        <id>tag:weather.gc.ca,2013-04-16:{index}</id>
        </entry>"""
        for index, (title, text) in enumerate(entries)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
    <updated>2026-06-16T14:26:57Z</updated>{body}</feed>"""


class WeatherEndpointTestCase(TestCase):

    def ingest(self, xml):
        with patch(GET_REQUEST, return_value=xml):
            return self.client.post("/weather/").json()


class TestSavingFeeds(WeatherEndpointTestCase):

    def test_same_feed_twice__is_only_saved_once(self):
        first = self.ingest(valid_weather_api_response)
        second = self.ingest(valid_weather_api_response)

        self.assertTrue(first["success"])
        self.assertFalse(second["success"])
        self.assertEqual(WeatherReport.objects.count(), 6)

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


class TestDailyConditions(WeatherEndpointTestCase):

    def daily_conditions(self):
        response = self.client.get("/weather-report/")
        self.assertEqual(response.status_code, 200)
        return response.json()["daily_conditions"]

    def test_real_feed__gives_each_regions_conditions(self):
        self.ingest(valid_weather_api_response)

        western, eastern = self.daily_conditions()

        self.assertEqual(
            eastern,
            {
                "region": {
                    "id": "eastern_lake_superior",
                    "name": "Eastern Lake Superior",
                },
                "wind": {
                    "state": "reported",
                    "from_direction": "south",
                    "speed_knots": 15.0,
                },
                "peak_wave_height_m": 1.0,
                "visibility": None,
            },
        )
        self.assertEqual(western["region"]["id"], "western_lake_superior")
        self.assertEqual(western["wind"]["from_direction"], "northwest")

    def test_region_with_no_reports__is_present_and_unknown(self):
        self.ingest(
            feed(
                ("Forecast for Today - Eastern Lake Superior", "Wind west 10 knots."),
                ("Waves for Today - Eastern Lake Superior", "Waves 1 metre."),
            )
        )

        western, eastern = self.daily_conditions()

        self.assertEqual(eastern["region"]["id"], "eastern_lake_superior")
        self.assertEqual(
            western,
            {
                "region": {
                    "id": "western_lake_superior",
                    "name": "Western Lake Superior",
                },
                "wind": {
                    "state": "unknown",
                    "from_direction": None,
                    "speed_knots": None,
                },
                "peak_wave_height_m": None,
                "visibility": None,
            },
        )

    def test_no_stored_reports__gives_both_regions_and_no_update_time(self):
        response = self.client.get("/weather-report/").json()

        self.assertIsNone(response["updated_at"])
        self.assertEqual(
            [c["region"]["id"] for c in response["daily_conditions"]],
            ["western_lake_superior", "eastern_lake_superior"],
        )

    def test_updated_at__is_the_feeds_update_time_in_utc(self):
        self.ingest(valid_weather_api_response)

        response = self.client.get("/weather-report/").json()

        self.assertEqual(response["updated_at"], "2026-02-16T15:26:57Z")

    def test_visibility__comes_from_the_forecast(self):
        self.ingest(
            feed(
                (
                    "Forecast for Today - Eastern Lake Superior",
                    "Wind west 10 knots. Visibility 1 mile or less in fog.",
                ),
                ("Extended Forecast - Eastern Lake Superior", "Friday: Wind light."),
            )
        )

        _, eastern = self.daily_conditions()

        self.assertEqual(eastern["visibility"], "1 mile or less in fog")

    def test_light_and_variable_wind__keep_their_state(self):
        self.ingest(
            feed(
                ("Forecast for Today - Eastern Lake Superior", "Wind light tonight."),
                (
                    "Forecast for Today - Western Lake Superior",
                    "Wind variable 10 knots.",
                ),
            )
        )

        western, eastern = self.daily_conditions()

        self.assertEqual(eastern["wind"]["state"], "light")
        self.assertIsNone(eastern["wind"]["from_direction"])
        self.assertEqual(western["wind"]["state"], "variable")
        self.assertEqual(western["wind"]["speed_knots"], 10.0)

    def test_whole_lake_warning__gets_no_card_and_does_not_crash(self):
        self.ingest(
            feed(
                ("STRONG WIND WARNING IN EFFECT, Lake Superior", ""),
                ("Forecast for Today - Eastern Lake Superior", "Wind west 10 knots."),
            )
        )

        self.assertEqual(
            [c["region"]["id"] for c in self.daily_conditions()],
            ["western_lake_superior", "eastern_lake_superior"],
        )

    def test_region_missing_a_forecast__is_unknown_and_keeps_its_waves(self):
        self.ingest(
            feed(
                ("Waves for Today - Western Lake Superior", "Waves 2 metres."),
                ("Extended Forecast - Western Lake Superior", "Friday: Wind light."),
            )
        )

        western, _ = self.daily_conditions()

        self.assertEqual(western["wind"]["state"], "unknown")
        self.assertIsNone(western["wind"]["speed_knots"])
        self.assertEqual(western["peak_wave_height_m"], 2.0)

    def test_failed_database_read__is_a_503(self):
        with patch.object(
            WeatherReport.objects, "aggregate", side_effect=OperationalError
        ):
            response = self.client.get("/weather-report/")

        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["success"])
