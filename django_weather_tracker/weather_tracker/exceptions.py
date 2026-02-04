from rest_framework import status
from rest_framework.exceptions import APIException


class ScraperError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Scraper Error"
    default_code = "scraper_error"
