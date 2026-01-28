from datetime import datetime
from typing import Any

from weather_tracker.models import Region, ReportType, Category, WeatherReport
from weather_tracker.parsers.generic_parser import GenericParser


class MarineXmlAPIParser(GenericParser):

    def parse(self, raw_data):

        report_list = self.parse_webpage_and_create_reports(raw_data)

        return report_list

    def parse_webpage_and_create_reports(self, raw_report_dict):
        main_data = raw_report_dict.get("feed")
        entry_list = main_data.get("entry", [])

        report_list = [
            self.parse_weather_entry(
                main_data,
                entry,
            )
            for entry in entry_list
        ]

        return report_list

    def parse_weather_entry(self, main_data, entry_dict):
        if not main_data or not entry_dict:
            return None

        updated_str = main_data.get("updated")
        updated_time = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
        date = updated_time.date()

        published_time = entry_dict.get("published")
        weather_canada_id = entry_dict.get("id")
        link = entry_dict.get("link", {}).get("@href")  # webpage link,
        title = entry_dict.get("title", "")
        summary = entry_dict.get("summary", {}).get("#text", "")

        report_type = self.extract_report_type(title)
        report_region = self.extract_report_region(title)

        weather_report = WeatherReport(
            region=report_region,
            report_type=report_type,
            title=title,
            date=date,
            published_time=published_time,
            updated_time=updated_time,
            category=Category.MARINE,
            summary=summary,
            link=link,
            weather_canada_id=weather_canada_id,
        )

        return weather_report

    def extract_report_type(self, title: str) -> ReportType:
        title = title.lower()

        if "extended forecast" in title:
            report_type = ReportType.EXTENDED
        elif "forecast for" in title:
            report_type = ReportType.DETAILED
        elif "waves for" in title:
            report_type = ReportType.WAVES
        elif "freezing spray warning" in title:
            report_type = ReportType.FREEZING_SPRAY_WARNING
        elif "gale warning" in title:
            report_type = ReportType.GALE_WARNING
        else:
            self.logger.error(f"Unknown report type: {title}")
            report_type = ReportType.UNDEFINED

        return report_type

    @staticmethod
    def extract_report_region(title: str) -> Region:
        title = title.lower()

        if "western" in title:
            region = Region.WESTERN_LAKE_SUPERIOR
        elif "eastern" in title:
            region = Region.EASTERN_LAKE_SUPERIOR
        else:
            region = Region.UNDEFINED

        return region

    # ---- Summary parsing (format per ReportType; add logic when samples are available) ----

    def parse_summary(self, summary: str, report_type: ReportType) -> dict[str, Any] | None:
        """
        Parse the summary text into a structured dict based on report_type.
        Returns None for UNDEFINED or on parse failure.
        """
        if not (summary or "").strip():
            return None
        if report_type == ReportType.UNDEFINED:
            return None
        try:
            if report_type == ReportType.DETAILED:
                return self._parse_detailed_summary(summary)
            if report_type == ReportType.WAVES:
                return self._parse_waves_summary(summary)
            if report_type == ReportType.EXTENDED:
                return self._parse_extended_summary(summary)
            if report_type == ReportType.FREEZING_SPRAY_WARNING:
                return self._parse_freezing_spray_warning_summary(summary)
            if report_type == ReportType.GALE_WARNING:
                return self._parse_gale_warning_summary(summary)
        except Exception as e:
            self.logger.warning("Summary parse failed for %s: %s", report_type, e)
            return None
        return None

    def _parse_detailed_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.DETAILED. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}

    def _parse_waves_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.WAVES. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}

    def _parse_extended_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.EXTENDED. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}

    def _parse_freezing_spray_warning_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.FREEZING_SPRAY_WARNING. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}

    def _parse_gale_warning_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.GALE_WARNING. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}
