from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_tracker.db_managers.weather_report_manager import WeatherReportManager
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherScraper
from weather_tracker.serializers.weather_report_serializer import (
    WeatherReportSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")
class WeatherForecastView(APIView):
    http_method_names = ["get", "post"]

    def get(self, request):
        weather_report_list = GovWeatherScraper().get()
        serializer = WeatherReportSerializer(weather_report_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        weather_report_list = GovWeatherScraper().get()
        was_save_successful = WeatherReportManager().save_list(weather_report_list)
        content = {"success": was_save_successful}
        return JsonResponse(content)
