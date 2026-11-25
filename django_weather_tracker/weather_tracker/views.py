import structlog
from django.db import DatabaseError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_tracker.daily_conditions import build_daily_conditions
from weather_tracker.exceptions import ScraperError
from weather_tracker.db_managers.weather_report_manager import WeatherReportManager
from weather_tracker.parsers.marine_xml_api_parser import MarineXmlAPIParser
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherRequest
from weather_tracker.serializers.weather_report_serializer import (
    WeatherReportSerializer,
)

logger = structlog.get_logger(__name__)


class WeatherForecastView(APIView):
    http_method_names = ["get", "post"]

    def get(self, request: Request):
        weather_dict = GovWeatherRequest().get()
        weather_report_list = MarineXmlAPIParser().parse(weather_dict)
        serializer = WeatherReportSerializer(weather_report_list, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        try:
            weather_dict = GovWeatherRequest().get()
            weather_report_list = MarineXmlAPIParser().parse(weather_dict)
        except ScraperError:
            weather_report_list = []
        if not weather_report_list:
            logger.error("Could not read the marine feed")
            return Response(
                {"success": False, "info": "Could not read the marine feed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            saved, already_saved = WeatherReportManager().save_list(weather_report_list)
        except DatabaseError:
            logger.exception("Could not save the marine feed")
            return Response(
                {"success": False, "info": "Could not save the feed"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "success": True,
                "info": "Feed saved",
                "saved": saved,
                "already_saved": already_saved,
            }
        )


class DailyWeatherReportView(APIView):
    http_method_names = ["get"]

    def get(self, request: Request):
        logger.info("Daily Weather Report")

        try:
            latest_reports = WeatherReportManager().get_latest_weather_reports()
        except DatabaseError:
            logger.exception("Could not read daily weather reports")
            return Response(
                {"success": False, "info": "Weather data is unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"success": True, **build_daily_conditions(latest_reports)})
