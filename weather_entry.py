from flask import Flask

from flask_weather_tracker.weather_web_scraper import GovWeatherScraper

app = Flask(__name__)
app.json.sort_keys = False  # want WeatherReport returned as defined on class, not alphabetical


@app.route("/weather")
def weather():
    eastern_report, western_report = GovWeatherScraper().get()
    return {"east": eastern_report, "west": western_report}
