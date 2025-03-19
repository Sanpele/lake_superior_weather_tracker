from flask import Flask

from flask_weather_tracker.weather_web_scraper import GovWeatherScraper

app = Flask(__name__)
app.json.sort_keys = False  # want WeatherReport returned as defined on class, not alphabetical


@app.route("/weather")
def weather():
    weather_report = GovWeatherScraper().get()
    return weather_report.__dict__
