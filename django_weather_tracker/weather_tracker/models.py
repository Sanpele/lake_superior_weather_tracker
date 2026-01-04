from django.db import models


class Region(models.TextChoices):
    EASTERN_LAKE_SUPERIOR = "eastern_lake_superior"
    WESTERN_LAKE_SUPERIOR = "western_lake_superior"


class ReportType(models.TextChoices):
    DETAILED = "detailed"
    WAVES = "waves"
    EXTENDED = "extended"


class Category(models.TextChoices):
    MARINE = "marine"


class WeatherReport(models.Model):
    region = models.CharField(max_length=30, choices=Region.choices)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    title = models.CharField(max_length=255)
    date = models.DateField()
    published_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.TextField()
    link = models.URLField(max_length=255)
    weather_canada_id = models.CharField(max_length=255)
