from django.db import models


class Region(models.TextChoices):
    EASTERN_LAKE_SUPERIOR = "eastern_lake_superior"
    WESTERN_LAKE_SUPERIOR = "western_lake_superior"
    UNDEFINED = "undefined"


class ReportType(models.TextChoices):
    DETAILED = "detailed"
    WAVES = "waves"
    EXTENDED = "extended"
    FREEZING_SPRAY_WARNING = "FREEZING_SPRAY_WARNING"
    GALE_WARNING = "GALE_WARNING"
    UNDEFINED = "undefined"


class Category(models.TextChoices):
    MARINE = "marine"


class WeatherReport(models.Model):
    region = models.CharField(max_length=30, choices=Region.choices)
    report_type = models.CharField(max_length=40, choices=ReportType.choices)
    title = models.CharField(max_length=255)
    date = models.DateField()
    published_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.TextField()
    link = models.URLField(max_length=255)
    weather_canada_id = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["region", "report_type", "published_time"],
                name="unique_region_and_report_type",
            )
        ]
