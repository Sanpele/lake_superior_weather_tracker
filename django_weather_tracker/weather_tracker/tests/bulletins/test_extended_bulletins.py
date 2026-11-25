from django.test import SimpleTestCase

from weather_tracker.bulletin_interpretation import ReportType, interpret_bulletin
from weather_tracker.tests.bulletins.helpers import REAL_BULLETINS


class TestExtendedBulletins(SimpleTestCase):

    def test_real_extended_bulletins__keep_each_day(self):
        for bulletin in REAL_BULLETINS["extended"]:
            with self.subTest(text=bulletin["text"][:70]):
                conditions = interpret_bulletin(bulletin["title"], bulletin["text"])

                self.assertEqual(conditions.report_type, ReportType.EXTENDED)
                self.assertEqual(
                    [day.day for day in conditions.days], bulletin["expected_days"]
                )
                self.assertTrue(all(day.wind for day in conditions.days))
