"""
Export sample summary strings from WeatherReport by report_type.

Use this to share examples for implementing summary parsing:
  python manage.py dump_summary_samples --output summary_samples.json
  python manage.py dump_summary_samples --max-per-type 5 --output samples.json

Then provide the generated JSON (or paste samples per type) so parsers can be implemented.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from weather_tracker.models import WeatherReport


class Command(BaseCommand):
    help = "Dump sample summary text from DB, grouped by report_type, for parser development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            default="summary_samples.json",
            help="Output JSON file path (default: summary_samples.json)",
        )
        parser.add_argument(
            "--max-per-type",
            "-n",
            type=int,
            default=15,
            help="Max number of sample summaries per report_type (default: 15)",
        )
        parser.add_argument(
            "--dedupe",
            action="store_true",
            help="Only include unique summary strings per type (no exact duplicates).",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        max_per_type = options["max_per_type"]
        dedupe = options["dedupe"]

        by_type = {}
        for report in WeatherReport.objects.all().order_by("report_type", "published_time"):
            rtype = report.report_type
            if rtype not in by_type:
                by_type[rtype] = []
            if len(by_type[rtype]) >= max_per_type:
                continue
            raw = (report.summary or "").strip()
            if not raw:
                continue
            if dedupe and raw in (s for s in by_type[rtype]):
                continue
            by_type[rtype].append(raw)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(by_type, f, indent=2, ensure_ascii=False)

        total = sum(len(v) for v in by_type.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {total} samples for {len(by_type)} report types to {output_path}"
            )
        )
        for rtype, samples in sorted(by_type.items()):
            self.stdout.write(f"  {rtype}: {len(samples)} samples")
