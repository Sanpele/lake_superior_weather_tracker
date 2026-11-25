"""What each region's daily conditions mean when they leave the backend.

Every region is always present, western first. A value the Bulletins did not
give us is Unknown or null. Wind is named by the direction it blows from.
updated_at is when the newest feed we read was updated.
"""

from weather_tracker.bulletin_interpretation import Region, ReportType, WindState

_REGION_NAMES = {
    Region.WESTERN_LAKE_SUPERIOR: "Western Lake Superior",
    Region.EASTERN_LAKE_SUPERIOR: "Eastern Lake Superior",
}


def build_daily_conditions(reports) -> dict:
    return {
        "updated_at": max((r.last_seen_at for r in reports), default=None),
        "daily_conditions": [
            _region_conditions(region, name, reports)
            for region, name in _REGION_NAMES.items()
        ],
    }


def _region_conditions(region: Region, name: str, reports) -> dict:
    by_type = {r.report_type: r for r in reports if r.region == region}
    forecast = by_type.get(ReportType.DETAILED)
    waves = by_type.get(ReportType.WAVES)

    return {
        "region": {"id": region.value, "name": name},
        "wind": {
            "state": forecast.wind_state if forecast else WindState.UNKNOWN.value,
            "from_direction": forecast.wind_direction if forecast else None,
            "speed_knots": forecast.wind_speed_knots if forecast else None,
        },
        "peak_wave_height_m": waves.max_wave_height_m if waves else None,
        "visibility": forecast.visibility_text if forecast else None,
    }
