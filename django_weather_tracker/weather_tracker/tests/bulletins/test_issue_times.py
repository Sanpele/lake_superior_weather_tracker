from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import interpret_bulletin
from weather_tracker.tests.bulletins.helpers import WAVES_TITLE


class TestIssueTimes(SimpleTestCase):

    def test_est_and_edt__are_timezone_aware(self):
        cases = [
            (
                "Issued 10:30  AM EST 16 February 2026",
                -5,
                datetime(2026, 2, 16, 10, 30),
            ),
            ("Issued 6:30  PM EDT 13 June 2026", -4, datetime(2026, 6, 13, 18, 30)),
            ("Issued 12:00  PM EDT 13 June 2026", -4, datetime(2026, 6, 13, 12, 0)),
            ("Issued 12:15  AM EST 16 February 2026", -5, datetime(2026, 2, 16, 0, 15)),
        ]
        for line, offset, local in cases:
            with self.subTest(line=line):
                conditions = interpret_bulletin(
                    WAVES_TITLE, f"Waves 1 metre.<br/>{line}"
                )

                self.assertEqual(
                    conditions.issued_at,
                    local.replace(tzinfo=timezone(timedelta(hours=offset))),
                )

    def test_other_zone__has_unknown_issue_time_and_line_is_removed(self):
        conditions = interpret_bulletin(
            WAVES_TITLE, "Waves 1 metre.<br/>Issued 10:30  AM CDT 16 June 2026"
        )

        self.assertIsNone(conditions.issued_at)
        self.assertEqual(conditions.peak_wave_height_m, 1)
