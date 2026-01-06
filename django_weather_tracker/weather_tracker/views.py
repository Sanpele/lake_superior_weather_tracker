from datetime import datetime

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_tracker.models import WeatherReport, Region, ReportType, Category
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherScraper
from weather_tracker.serializers.weather_report_serializer import WeatherReportSerializer


@method_decorator(csrf_exempt, name="dispatch")
class WeatherForecastView(APIView):
    http_method_names = ["get", "post"]

    def get(self, request):
        weather_report_list = GovWeatherScraper().get()
        serializer = WeatherReportSerializer(weather_report_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        weather_report_list = GovWeatherScraper().get()

        today = datetime.now()
        today_date = today.date()

        WeatherReport.objects.create(
            region=Region.EASTERN_LAKE_SUPERIOR,
            report_type=ReportType.WAVES,
            title="placeholder",
            date=today_date,
            published_time=today,
            updated_time=today,
            category=Category.MARINE,
            summary="placeholder :)",
            link="https://www.weather.gc.ca/marine/forecast_e.html?mapID=09&siteID=08507#forecast",
            weather_canada_id="abc123",
        )
        content = {"placeholder": "yep"}

        return JsonResponse(content)
