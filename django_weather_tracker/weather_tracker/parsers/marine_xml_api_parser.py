import re
from datetime import datetime
from typing import Any

from weather_tracker.models import Region, ReportType, Category, WeatherReport
from weather_tracker.parsers.generic_parser import GenericParser

# Month name to number for "Issued DD Month YYYY"
_MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]


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

        summary_parsed = self._parsed_summary_for_db(summary, report_type)
        print(summary_parsed)
        
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

    # ---- Summary parsing ----

    _ISSUED_RE = re.compile(
        r"<br/>\s*Issued\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+EST\s+(\d{1,2})\s+(\w+)\s+(\d{4})\s*$",
        re.IGNORECASE,
    )

    @staticmethod
    def _parse_issued_line(text: str) -> dict[str, Any] | None:
        """
        Parse trailing 'Issued HH:MM AM/PM EST DD Month YYYY' from summary text.
        Returns dict with issued_raw (str), issued_at (datetime | None), and body (rest of text).
        """
        text = (text or "").strip()
        if not text:
            return {"body": "", "issued_raw": "", "issued_at": None}
        m = MarineXmlAPIParser._ISSUED_RE.search(text)
        if not m:
            return {"body": text, "issued_raw": "", "issued_at": None}
        hour, minute, ampm, day, month_name, year = m.groups()
        body = text[: m.start()].strip()
        issued_raw = m.group(0).replace("<br/>", "").strip()
        hour_i = int(hour)
        if ampm.upper() == "PM" and hour_i != 12:
            hour_i += 12
        elif ampm.upper() == "AM" and hour_i == 12:
            hour_i = 0
        month_lower = month_name.lower()
        try:
            month_i = _MONTH_NAMES.index(month_lower) + 1
        except ValueError:
            month_i = 1
        try:
            issued_at = datetime(int(year), month_i, int(day), hour_i, int(minute))
        except (ValueError, TypeError):
            issued_at = None
        return {"body": body, "issued_raw": issued_raw, "issued_at": issued_at}

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
        """
        Parse detailed forecast: wind paragraph, precipitation/visibility/freezing-spray
        blocks (double-space separated), and trailing Issued line.
        """
        out = self._parse_issued_line(summary)
        body = out["body"].replace("\n", " ")
        # Split on double space into blocks; first block is wind, rest are conditions
        blocks = [b.strip() for b in re.split(r"\s{2,}", body) if b.strip()]
        wind_text = ""
        conditions: list[str] = []
        for block in blocks:
            if block.lower().startswith("wind ") and not wind_text:
                wind_text = block
            else:
                conditions.append(block)
        return {
            "wind": wind_text,
            "conditions": conditions,
            "issued_raw": out["issued_raw"],
            "issued_at": out["issued_at"],
            "raw": summary,
        }

    def _parse_waves_summary(self, summary: str) -> dict[str, Any]:
        """
        Parse waves summary: wave height phrases (e.g. "1 metre building to 1.5 Tuesday
        morning") and optional Issued line. Returns wave_phrases (list of str) and
        parsed heights when detectable (e.g. {"min": 1, "max": 1.5, "unit": "m"}).
        """
        out = self._parse_issued_line(summary)
        body = out["body"].replace("\n", " ").strip()
        # Split into sentences (period or <br/>); keep only "Waves ..." phrases
        parts = re.split(r"\.\s+|<br/>\s*", body)
        wave_phrases = [p.strip() for p in parts if p.strip().lower().startswith("waves ")]
        # Optionally parse numeric heights: "1 metre", "1.5", "0.5 to 1", "1 to 1.5", "0.5 or less"
        height_re = re.compile(
            r"(\d+(?:\.\d+)?)\s*(?:\s+to\s+(\d+(?:\.\d+)?)|\s+or\s+less)?\s*(?:metre|metres)?",
            re.IGNORECASE,
        )
        heights: list[dict[str, Any]] = []
        for phrase in wave_phrases:
            for m in height_re.finditer(phrase):
                g = m.groups()
                if g[1]:
                    heights.append({"min": float(g[0]), "max": float(g[1]), "unit": "m"})
                elif "or less" in phrase[m.start() : m.end() + 20].lower():
                    heights.append({"max": float(g[0]), "unit": "m"})
                else:
                    heights.append({"value": float(g[0]), "unit": "m"})
        return {
            "wave_phrases": wave_phrases,
            "heights": heights,
            "issued_raw": out["issued_raw"],
            "issued_at": out["issued_at"],
            "raw": summary,
        }

    def _parse_extended_summary(self, summary: str) -> dict[str, Any]:
        """
        Parse extended forecast: day blocks "DayName: Wind ..." separated by <br/>,
        then Issued line.
        """
        out = self._parse_issued_line(summary)
        body = out["body"].replace("\n", " ")
        # Split by <br/> and parse "Weekday: Wind ..." or "Weekday: Wind light."
        day_re = re.compile(r"^(\w+):\s*(.+)$", re.IGNORECASE)
        days: list[dict[str, str]] = []
        for segment in re.split(r"<br/>\s*", body):
            segment = segment.strip()
            if not segment or segment.lower().startswith("issued"):
                continue
            mo = day_re.match(segment)
            if mo:
                days.append({"day": mo.group(1), "wind": mo.group(2).strip()})
            elif segment:
                days.append({"day": "", "wind": segment})
        return {
            "days": days,
            "issued_raw": out["issued_raw"],
            "issued_at": out["issued_at"],
            "raw": summary,
        }

    def _parse_freezing_spray_warning_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.FREEZING_SPRAY_WARNING. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}

    def _parse_gale_warning_summary(self, summary: str) -> dict[str, Any]:
        """Parse summary for ReportType.GALE_WARNING. Format TBD from samples."""
        # TODO: implement once sample format is known
        return {"raw": summary}
