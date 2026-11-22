"""
Rebuild each WeatherReport's parsed fields from its stored Bulletin.

Reports what would change by default:
  python manage.py reinterpret_bulletins

Saves the changes in one transaction, or aborts on any conflict:
  python manage.py reinterpret_bulletins --apply
"""

from collections import Counter, defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from weather_tracker.bulletin_interpretation import interpret_bulletin
from weather_tracker.models import WeatherReport
from weather_tracker.parsers.marine_xml_api_parser import stored_fields

SAMPLES_PER_FIELD = 3


class Command(BaseCommand):
    help = "Rebuild parsed fields from stored Bulletins. Dry run unless --apply."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Save the changes. Without this, only report them.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        with transaction.atomic():
            reports = WeatherReport.objects.order_by("id")
            if apply_changes:
                reports = reports.select_for_update()
            reports = list(reports)

            changed, field_counts, samples, rows_by_key = self._plan(reports)
            conflicts = {k: ids for k, ids in rows_by_key.items() if len(ids) > 1}
            self._report(reports, changed, field_counts, samples, conflicts)

            if not apply_changes:
                self.stdout.write("Dry run: nothing was saved.")
                return
            if conflicts:
                raise CommandError(
                    "Aborted because of conflicts. Nothing was saved or deleted."
                )
            if changed:
                WeatherReport.objects.bulk_update(
                    changed, fields=sorted(field_counts), batch_size=500
                )

        self.stdout.write(self.style.SUCCESS(f"Saved {len(changed)} rows."))

    @staticmethod
    def _plan(reports):
        changed = []
        field_counts = Counter()
        samples = defaultdict(list)
        rows_by_key = defaultdict(list)

        for report in reports:
            fields = stored_fields(interpret_bulletin(report.title, report.summary))
            differences = {
                name: (getattr(report, name), value)
                for name, value in fields.items()
                if getattr(report, name) != value
            }
            for name, (old, new) in differences.items():
                field_counts[name] += 1
                if len(samples[name]) < SAMPLES_PER_FIELD:
                    samples[name].append(f"id {report.id}: {old!r} -> {new!r}")
                setattr(report, name, new)
            if differences:
                changed.append(report)

            key = (
                report.region,
                report.report_type,
                report.warning_status,
                report.published_time,
            )
            rows_by_key[key].append(report.id)

        return changed, field_counts, samples, rows_by_key

    def _report(self, reports, changed, field_counts, samples, conflicts):
        self.stdout.write(f"Rows scanned: {len(reports)}")
        self.stdout.write(f"Rows to change: {len(changed)}")
        for name, count in sorted(field_counts.items()):
            self.stdout.write(f"  {name}: {count}")
            for sample in samples[name]:
                self.stdout.write(f"    {sample}")

        self.stdout.write(f"Conflicts: {len(conflicts)}")
        for (region, report_type, status, published), ids in conflicts.items():
            self.stdout.write(
                f"  {region} {report_type} {status or '-'} {published}: rows {ids}"
            )
