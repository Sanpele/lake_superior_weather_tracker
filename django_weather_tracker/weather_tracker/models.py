from django.db import models

from weather_tracker.bulletin_interpretation import (
    Region,
    ReportType,
    WarningStatus,
    WindState,
)


def _choices(vocabulary):
    return [(item.value, item.name.replace("_", " ").title()) for item in vocabulary]


class Category(models.TextChoices):
    MARINE = "marine"
    AIR_QUALITY = "air_quality"


class WeatherReport(models.Model):
    region = models.CharField(max_length=30, choices=_choices(Region))
    report_type = models.CharField(max_length=40, choices=_choices(ReportType))
    title = models.CharField(max_length=255)
    date = models.DateField()
    published_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    # Update time of the newest feed this Bulletin appeared in
    last_seen_at = models.DateTimeField()
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.TextField()

    # Blank for anything that is not a Marine warning, so it stays in the unique key
    warning_status = models.CharField(
        max_length=10, choices=_choices(WarningStatus), blank=True, default=""
    )

    # Parsed "critical" fields from summary (nullable because they depend on report_type)
    wind_state = models.CharField(
        max_length=10, choices=_choices(WindState), default=WindState.UNKNOWN.value
    )
    wind_direction = models.CharField(max_length=32, null=True, blank=True)
    wind_speed_knots = models.FloatField(null=True, blank=True)
    max_wave_height_m = models.FloatField(null=True, blank=True)
    visibility_text = models.CharField(max_length=255, null=True, blank=True)

    link = models.URLField(max_length=255)
    weather_canada_id = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["region", "report_type", "warning_status", "published_time"],
                name="unique_region_type_status_published",
            )
        ]
