from django.db import migrations, models


def last_seen_in_own_feed(apps, schema_editor):
    WeatherReport = apps.get_model("weather_tracker", "WeatherReport")
    WeatherReport.objects.update(last_seen_at=models.F("updated_time"))


class Migration(migrations.Migration):

    dependencies = [
        ("weather_tracker", "0006_bulletin_conditions"),
    ]

    operations = [
        migrations.AddField(
            model_name="weatherreport",
            name="last_seen_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(last_seen_in_own_feed, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="weatherreport",
            name="last_seen_at",
            field=models.DateTimeField(),
        ),
    ]
