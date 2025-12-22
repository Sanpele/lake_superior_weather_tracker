from dataclasses import asdict

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views import View

from weather_tracker.scraping_logic.weather_web_scraper import GovWeatherScraper


class WeatherForecastView(View):

    def get(self, request):
        eastern_report, western_report = GovWeatherScraper().get()
        content = {"east": asdict(eastern_report), "west": asdict(western_report)}
        return JsonResponse(content, encoder=DjangoJSONEncoder)
