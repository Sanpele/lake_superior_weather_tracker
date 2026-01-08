from rest_framework import serializers

from weather_tracker.models import WeatherReport


class WeatherReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherReport
        fields = "__all__"
