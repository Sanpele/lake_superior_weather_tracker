from django.http import HttpResponse
from django.views import View

from django_weather_tracker.weather_tracker.scraping_logic.weather_web_scraper import GovWeatherScraper


class WeatherForecastView(View):

    def get(self, request):
        eastern_report, western_report = GovWeatherScraper().get()
        content = {"east": eastern_report, "west": western_report}
        return HttpResponse(content=content)
