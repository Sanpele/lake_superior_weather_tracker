from dataclasses import asdict
from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from weather_tracker.models import WeatherReport, Region, ReportType, Category
from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherScraper


@method_decorator(csrf_exempt, name="dispatch")
class WeatherForecastView(View):
    http_method_names = ["get", "post"]

    def get(self, request):
        eastern_report, western_report = GovWeatherScraper().get()
        content = {"east": asdict(eastern_report), "west": asdict(western_report)}
        return JsonResponse(content, encoder=DjangoJSONEncoder)

    def post(self, request):
        eastern_report, western_report = GovWeatherScraper().get()

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
