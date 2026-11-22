from unittest.mock import patch

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

    def daily_reports(self):
        response = self.client.get("/weather-report/")
        self.assertEqual(response.status_code, 200)
        return {r["region"]: r for r in response.json()["daily_reports"]}


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


class TestDailyReport(WeatherEndpointTestCase):

    def test_real_feed__gives_each_regions_conditions(self):
        self.ingest(valid_weather_api_response)

        reports = self.daily_reports()

        self.assertEqual(
            reports["eastern_lake_superior"],
            {
                "region": "eastern_lake_superior",
                "wind_state": "reported",
                "wind_direction": "south",
                "wind_speed": 15.0,
                "wave_height": 1.0,
                "visibility": None,
            },
        )
        self.assertEqual(
            reports["western_lake_superior"]["wind_direction"], "northwest"
        )

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

        report = self.daily_reports()["eastern_lake_superior"]

        self.assertEqual(report["visibility"], "1 mile or less in fog")

    def test_light_and_variable_wind__are_in_the_payload(self):
        self.ingest(
            feed(
                ("Forecast for Today - Eastern Lake Superior", "Wind light tonight."),
                (
                    "Forecast for Today - Western Lake Superior",
                    "Wind variable 10 knots.",
                ),
            )
        )

        reports = self.daily_reports()

        self.assertEqual(reports["eastern_lake_superior"]["wind_state"], "light")
        self.assertIsNone(reports["eastern_lake_superior"]["wind_direction"])
        self.assertEqual(reports["western_lake_superior"]["wind_state"], "variable")
        self.assertEqual(reports["western_lake_superior"]["wind_speed"], 10.0)

    def test_whole_lake_warning__gets_no_card_and_does_not_crash(self):
        self.ingest(
            feed(
                ("STRONG WIND WARNING IN EFFECT, Lake Superior", ""),
                ("Forecast for Today - Eastern Lake Superior", "Wind west 10 knots."),
            )
        )

        self.assertEqual(list(self.daily_reports()), ["eastern_lake_superior"])

    def test_region_missing_a_forecast__is_unknown_and_does_not_crash(self):
        self.ingest(
            feed(
                ("Waves for Today - Western Lake Superior", "Waves 2 metres."),
                ("Extended Forecast - Western Lake Superior", "Friday: Wind light."),
            )
        )

        report = self.daily_reports()["western_lake_superior"]

        self.assertEqual(report["wind_state"], "unknown")
        self.assertIsNone(report["wind_speed"])
        self.assertEqual(report["wave_height"], 2.0)
