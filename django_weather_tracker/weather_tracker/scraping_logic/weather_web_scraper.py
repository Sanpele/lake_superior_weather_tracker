import logging

import xmltodict

from weather_tracker.exceptions import ScraperError
from weather_tracker.utils import get_request


class GovWeatherRequest:

    XML_URL = "https://weather.gc.ca/rss/marine/08500_e.xml"
    logger = logging.getLogger(__name__)

    def get(self):
        try:
            weather_xml = get_request(self.XML_URL)
            weather_dict = xmltodict.parse(weather_xml)
            return weather_dict
        except Exception as e:
            self.logger.error(e)
            raise ScraperError()
