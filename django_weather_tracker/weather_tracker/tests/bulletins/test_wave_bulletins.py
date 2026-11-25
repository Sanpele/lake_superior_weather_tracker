from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import ReportType, interpret_bulletin
from weather_tracker.tests.bulletins.helpers import REAL_BULLETINS, WAVES_TITLE


class TestWaveBulletins(SimpleTestCase):

    def test_real_wave_bulletins__give_peak_height(self):
        for bulletin in REAL_BULLETINS["waves"]:
            with self.subTest(text=bulletin["text"][:70]):
                conditions = interpret_bulletin(bulletin["title"], bulletin["text"])

                self.assertEqual(conditions.report_type, ReportType.WAVES)
                self.assertEqual(
                    conditions.peak_wave_height_m, bulletin["expected_peak_m"]
                )

    def test_peak_height__includes_except_clause(self):
        conditions = interpret_bulletin(
            WAVES_TITLE, "Waves 1 to 1.5 metres except 2 over northern sections."
        )

        self.assertEqual(conditions.peak_wave_height_m, 2)

    def test_edt_issue_line__is_not_read_as_a_wave_height(self):
        conditions = interpret_bulletin(
            WAVES_TITLE,
            "Waves 1 metre.<br/>Issued 10:30  AM EDT 16 June 2026",
        )

        self.assertEqual(conditions.peak_wave_height_m, 1)

    def test_wave_text_without_a_height__is_unknown_and_logged(self):
        text = "Waves unavailable."

        with self.assertLogs(
            "weather_tracker.bulletin_interpretation", level="WARNING"
        ) as logs:
            conditions = interpret_bulletin(WAVES_TITLE, text)

        self.assertIsNone(conditions.peak_wave_height_m)
        self.assertIn(text, logs.output[0])
