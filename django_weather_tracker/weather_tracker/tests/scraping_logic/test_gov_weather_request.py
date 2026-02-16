from django.test import SimpleTestCase
from unittest.mock import patch

from rest_framework import status

from weather_tracker.exceptions import ScraperError
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherRequest
from weather_tracker.tests.testing_mocks import valid_weather_api_response


class TestGovWeatherRequest(SimpleTestCase):

    @patch(
        "weather_tracker.scraping_logic.weather_web_scraper.get_request",
        return_value=valid_weather_api_response,
    )
    def test_gov_weather_request__valid_request__parses_successfully(
        self, _mock_get_request
    ):
        weather_dict = GovWeatherRequest().get()

        self.assertTrue(isinstance(weather_dict, dict))
        self.assertEqual(weather_dict["feed"]["author"]["name"], "Environment Canada")

    @patch(
        "weather_tracker.scraping_logic.weather_web_scraper.get_request",
        side_effect=Exception("API ERROR"),
    )
    def test_gov_weather_request__invalid_request__raises_scraper_error(self, _):

        with self.assertRaises(ScraperError) as e:
            GovWeatherRequest().get()

        self.assertTrue(isinstance(e.exception, ScraperError))
        self.assertEqual(e.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
