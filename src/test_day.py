from day import *
from timeslot import *
from unittest import TestCase
import arrow

class DayTest(TestCase):
    def test_values(self):
        dateString = "13.05.2023"
        date = arrow.get(dateString,"DD.MM.YYYY")
        timeslots = [TimeSlot.fromString("09:00 - 12:30"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("18:00 - 23:00")]
        day = Day(date, timeslots)

        self.assertEqual(day.date, date, "Wrong date")
        self.assertEqual(day.dateString, dateString, "Wrong Datestring")
        self.assertEqual(day.timeInMinutes(), 570, "Wrong day length")

        self.assertEqual(day.day, int(dateString[:2]), "Wrong Day")
        self.assertEqual(day.month, int(dateString[3:5]), "Wrong Month")
        self.assertEqual(day.year, int(dateString[6:]), "Wrong Year")

        values = day.export()

        self.assertEqual(values["dateString"], dateString, "Wrong Datestring in Export")
        self.assertEqual(values["timeslots"], timeslots, "Wrong list of timeslots in Export")

    def test_comparison(self):
        day1 = Day(arrow.get("17.06.2021","DD.MM.YYYY"), [])
        day2 = Day(arrow.get("24.03.2020","DD.MM.YYYY"), [])
        self.assertGreater(day1, day2, "Comparison #1")
        self.assertGreaterEqual(day1, day2, "Comparison #2")
        self.assertLess(day2, day1, "Comparison #3")
        self.assertLessEqual(day2, day1, "Comparison #4")
        self.assertNotEqual(day1, day2, "Comparison #5")

        self.assertEqual(day1, day1, "Comparison #6")

        day3 = Day(arrow.get("17.06.2021","DD.MM.YYYY"), [])
        self.assertNotEqual(day1, day2, "Comparison #7") # There should be no equal dates, so == should only check for SAME
