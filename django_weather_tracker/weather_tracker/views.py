from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_tracker.db_managers.weather_report_manager import WeatherReportManager
from weather_tracker.parsers.marine_xml_api_parser import MarineXmlAPIParser
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherRequest
from weather_tracker.serializers.weather_report_serializer import (
    WeatherReportSerializer,
)


class WeatherForecastView(APIView):
    http_method_names = ["get", "post"]

    def get(self, request):
        weather_dict = GovWeatherRequest().get()
        weather_report_list = MarineXmlAPIParser().parse(weather_dict)

        serializer = WeatherReportSerializer(weather_report_list, many=True)

        return Response(serializer.data)

    def post(self, request):
        weather_dict = GovWeatherRequest().get()
        weather_report_list = MarineXmlAPIParser().parse(weather_dict)
        was_save_successful = WeatherReportManager().save_list(weather_report_list)

        content = {"success": was_save_successful}

        return JsonResponse(content)
