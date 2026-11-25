from unittest.mock import patch

from django.test import TestCase


GET_REQUEST = "weather_tracker.scraping_logic.weather_web_scraper.get_request"
ISSUE_LINE = "&#60;br/>Issued 10:30  AM EDT 16 June 2026"
FEED_UPDATED = "2026-06-16T14:26:57Z"
LATER_FEED_UPDATED = "2026-06-16T20:26:57Z"
PUBLISHED = "2026-06-16T14:30:00Z"
LATER_PUBLISHED = "2026-06-16T20:30:00Z"

EASTERN_FORECAST = (
    "Forecast for Today - Eastern Lake Superior",
    "Wind south 15 knots.",
)

EASTERN_EXTENDED = (
    "Extended Forecast - Eastern Lake Superior",
    "Friday: Wind light.",
    "2026-06-16T12:00:00Z",
)


def entry(index, title, text, published=PUBLISHED):
    return f"""<entry>
        <title>{title}</title>
        <link type="text/html" href="https://www.weather.gc.ca/marine"/>
        <published>{published}</published>
        <summary type="html">{text}{ISSUE_LINE}</summary>
        <id>tag:weather.gc.ca,2013-04-16:{index}</id>
        </entry>"""


def feed(*entries, updated=FEED_UPDATED):
    body = "".join(entry(index, *e) for index, e in enumerate(entries))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
    <updated>{updated}</updated>{body}</feed>"""


class WeatherEndpointTestCase(TestCase):

    def ingest(self, xml):
        with patch(GET_REQUEST, return_value=xml):
            return self.client.post("/weather/").json()

    def daily_conditions(self):
        response = self.client.get("/weather-report/")
        self.assertEqual(response.status_code, 200)
        return response.json()["daily_conditions"]
