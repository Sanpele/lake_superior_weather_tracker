from collections import defaultdict

import structlog
from django.db import DatabaseError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_tracker.daily_conditions import build_daily_conditions
from weather_tracker.db_managers.weather_report_manager import (
    DAILY_REPORT_REGIONS,
    WeatherReportManager,
)
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
        weather_dict = GovWeatherRequest().get()
        weather_report_list = MarineXmlAPIParser().parse(weather_dict)
        was_save_successful, reason = WeatherReportManager().save_list(
            weather_report_list
        )
        content = {"success": was_save_successful, "info": reason}
        return JsonResponse(content)


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

        grouped = defaultdict(list)

        for row in latest_reports:
            if row.region in DAILY_REPORT_REGIONS:
                grouped[row.region].append(row)

        response = []
        for region, rows in grouped.items():
            response.append(WeatherReportManager().build_daily_report_summary(rows))

        return Response(
            {
                "success": True,
                "daily_reports": response,
                **build_daily_conditions(latest_reports),
            }
        )
