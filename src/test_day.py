from day import *
from timeslot import *
from appointment import Appointment
from unittest import TestCase
import arrow

class DayTest(TestCase):
    def test_values(self):
        dateString = "13.05.2023"
        date = arrow.get(dateString,"DD.MM.YYYY")
        timeslots = [TimeSlot.fromString("09:00 - 12:30"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("18:00 - 23:00")]
        day = Day(date, timeslots, [])

        self.assertEqual(day.date, date, "Wrong date")
        self.assertEqual(day.dateString, dateString, "Wrong Datestring")
        self.assertEqual(day.timeInMinutes(), 570, "Wrong day length")

        self.assertEqual(day.day, int(dateString[:2]), "Wrong Day")
        self.assertEqual(day.month, int(dateString[3:5]), "Wrong Month")
        self.assertEqual(day.year, int(dateString[6:]), "Wrong Year")

        values = day.export()

        self.assertEqual(values["dateString"], dateString, "Wrong Datestring in Export")

    def test_comparison(self):
        day1 = Day(arrow.get("17.06.2021","DD.MM.YYYY"), [], [])
        day2 = Day(arrow.get("24.03.2020","DD.MM.YYYY"), [], [])
        self.assertGreater(day1, day2, "Comparison #1")
        self.assertGreaterEqual(day1, day2, "Comparison #2")
        self.assertLess(day2, day1, "Comparison #3")
        self.assertLessEqual(day2, day1, "Comparison #4")
        self.assertNotEqual(day1, day2, "Comparison #5")

        self.assertEqual(day1, day1, "Comparison #6")

        day3 = Day(arrow.get("17.06.2021", "DD.MM.YYYY"), [], [])
        self.assertNotEqual(day1, day2, "Comparison #7") # There should be no equal dates, so == should only check for SAME

    def test_timeslots(self):
        timeslots = [TimeSlot.fromString("09:00 - 12:30"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("18:00 - 23:00")]
        day1 = Day(arrow.get("17.06.2021", "DD.MM.YYYY"), timeslots, [])
        self.assertEqual(timeslots, day1.timeSlots, "TimeSlots are not initialised correctly")
        timeSlot = TimeSlot.fromString("15:30 - 17:30")
        day1.addTimeSlot(timeSlot)
        self.assertIn(timeSlot, day1.timeSlots, "Timeslot not added to semi-filled day correctly")
        self.assertEqual(day1.timeInMinutes(), 690, "Time not calculated correctly after timeslot was added to semi-filled day")

        day2 = Day(arrow.get("23.09.2021", "DD.MM.YYYY"), [], [])
        timeSlot = TimeSlot.fromString("15:30 - 17:30")
        day2.addTimeSlot(timeSlot)
        self.assertEqual(timeSlot, day2.timeSlots[0], "TimeSlot not added to empty day correctly")
        self.assertEqual(day2.timeInMinutes(), 120, "Time not calculated correctly after timeslot was added to empty day")
        
    def test_appointment(self):
        day1 = Day(arrow.get("01.01.2021", "DD.MM.YYYY"), [], [])
        app1 = Appointment("Test-Appointment", TimeSlot.fromString("09:00 - 12:30"))
        day1.addAppointment(app1)
        self.assertIn(app1, day1.appointments, "Appointment not added correctly to empty day")

        apps = [
            Appointment("Alpha-Appointment", TimeSlot.fromString("09:00 - 12:30")),
            Appointment("Beta-Appointment", TimeSlot.fromString("14:00 - 16:30")), # Overlapping appointments are okay
            Appointment("Gamma-Appointment", TimeSlot.fromString("13:00 - 15:30"))
        ]

        day2 = Day(arrow.get("01.12.2021", "DD.MM.YYYY"), [], apps)
        self.assertEqual(apps, day2.appointments, "Appointments are not initialised correctly")

        app2 = Appointment("Test-Appointment", TimeSlot.fromString("18:00 - 21:30"))
        day2.addAppointment(app2)
        self.assertIn(app2, day2.appointments, "Appointment was not added correctly to semi-filled day")

    def test_invalid_timeslots(self):
        day1 = Day(arrow.get("01.01.2021", "DD.MM.YYYY"), [], [])
        ts1 = TimeSlot.fromString("09:00 - 12:30")
        ts2 = TimeSlot.fromString("09:00 - 12:30")
        day1.addTimeSlot(ts1)
        self.assertRaises(ValueError, day1.addTimeSlot, ts2)

        ts3 = TimeSlot.fromString("07:00 - 9:30") # Scenario [{]}
        self.assertRaises(ValueError, day1.addTimeSlot, ts3)

        ts4 = TimeSlot.fromString("12:00 - 15:30") # Scenario {[}]
        self.assertRaises(ValueError, day1.addTimeSlot, ts4)

        ts5 = TimeSlot.fromString("08:00 - 13:30") # Scenario [{}]
        self.assertRaises(ValueError, day1.addTimeSlot, ts5)

        ts6 = TimeSlot.fromString("09:00 - 12:30") # Scenario equal
        self.assertRaises(ValueError, day1.addTimeSlot, ts6)

        ts7 = TimeSlot.fromString("09:00 - 13:30") # Scenario {[}] (tight start)
        self.assertRaises(ValueError, day1.addTimeSlot, ts7)

        ts8 = TimeSlot.fromString("11:00 - 12:30") # Scenario [{]} (tight end)
        self.assertRaises(ValueError, day1.addTimeSlot, ts8)

        ts9 = TimeSlot.fromString("10:30 - 12:00") # Scenario {[]}
        self.assertRaises(ValueError, day1.addTimeSlot, ts9)

        self.assertEqual(len(day1.timeSlots), 1, "One of the invalid timeslots was added despite throwing an error")

        ts10 = TimeSlot.fromString("14:00 - 16:00") # Valid
        day1.addTimeSlot(ts10)
        self.assertIn(ts10, day1.timeSlots, "TS10 was not added correctly!")
        self.assertEqual(len(day1.timeSlots), 2, f"Incorrect amount of timeslots ({len(day1.timeSlots)})!")

    def test_freeTime(self):
        timeslots = [TimeSlot.fromString("09:00 - 12:30"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("18:00 - 23:00")]
        day1 = Day("04.09.2021", timeslots, [])
        
        self.assertEqual(day1.timeInMinutes(), day1.freeTimeInMinutes(), "Time and FreeTime should be equal when there are no appointments")
        self.assertEqual(day1.freeTimeInMinutes(), 570, "Free Time is incorrect at the start. Maybe a test-issue?")

        app1 = Appointment("Gamma-Appointment", TimeSlot.fromString("13:00 - 15:30")) # Scenario {[]}, tight start
        day1.addAppointment(app1)
        self.assertEqual(day1.freeTimeInMinutes(), 510, f"Free time should have accounted for Appointment overlap; Expected 510, Got {day1.freeTimeInMinutes()}")

        app2 = Appointment("Yolo-Appointment", TimeSlot.fromString("13:30 - 14:30"))
        day1.addAppointment(app2)
        app3 = Appointment("Yana-Appointment", TimeSlot.fromString("04:00 - 7:30"))
        day1.addAppointment(app3)
        self.assertEqual(day1.freeTimeInMinutes(), 510, "Free Time should not have changed after non-overlapping appointments were added!")

        app4 = Appointment("Intermediate-Appointment", TimeSlot.fromString("10:00 - 10:30")) # Scenario [{}]
        day1.addAppointment(app4)
        self.assertEqual(day1.freeTimeInMinutes(), 480, "Free Time not calculated correctly after in-the-middle appointment was added")

        app5 = Appointment("Ending-Appointment", TimeSlot.fromString("12:00 - 13:30")) # Scenario [{]}
        day1.addAppointment(app5)
        self.assertEqual(day1.freeTimeInMinutes(), 450, "Free Time not calculated correctly after end-overlapping appointment was added")

        app6 = Appointment("Starting-Appointment", TimeSlot.fromString("08:00 - 09:30")) # Scenario {[}]
        day1.addAppointment(app6)
        self.assertEqual(day1.freeTimeInMinutes(), 420, "Free Time not calculated correctly after end-overlapping appointment was added")

    def test_freeTime2(self):
        timeslots = [TimeSlot.fromString("06:00 - 11:00"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("16:00 - 20:00")]
        day1 = Day("13.09.2021", timeslots, [])
        self.assertEqual(day1.freeTimeInMinutes(), 600, "Free Time is incorrect at the start. Maybe a test-issue?")
        
        app1 = Appointment("Some-Appointment", TimeSlot.fromString("12:00 - 14:00")) # Scenario {[]}, tight end
        day1.addAppointment(app1)
        self.assertEqual(day1.freeTimeInMinutes(), 540, "Free Time is incorrect after CASE 1")

        app2 = Appointment("Some-Appointment", TimeSlot.fromString("06:00 - 11:00")) # Scenario {[]}, EQUAL
        day1.addAppointment(app2)
        self.assertEqual(day1.freeTimeInMinutes(), 240, "Free Time is incorrect after CASE 2")

    def test_freeTime3(self):
        timeslots = [TimeSlot.fromString("06:00 - 11:00"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("16:00 - 20:00")]
        day1 = Day("30.01.2021", timeslots, [])
        self.assertEqual(day1.freeTimeInMinutes(), 600, "Free Time is incorrect at the start. Maybe a test-issue?")
        
        app1 = Appointment("Multi-Appointment", TimeSlot.fromString("13:30 - 17:30")) # Multioverlap
        day1.addAppointment(app1)
        self.assertEqual(day1.freeTimeInMinutes(), 480, "Free Time is incorrect after MULTI-OVERLAP")

        app2 = Appointment("Containing-Appointment", TimeSlot.fromString("05:00 - 18:00")) # Multicontaining
        day1.addAppointment(app2)
        self.assertEqual(day1.freeTimeInMinutes(), 120, "Free Time is incorrect after MULTI-CONTAINING")

    def test_freeTime4(self):
        timeslots = [TimeSlot.fromString("06:00 - 11:00"), TimeSlot.fromString("13:00 - 14:00"), TimeSlot.fromString("16:00 - 20:00")]
        day1 = Day("24.02.2021", timeslots, [])
        self.assertEqual(day1.freeTimeInMinutes(), 600, "Free Time is incorrect at the start. Maybe a test-issue?")

        app1 = Appointment("Bonus-Appointment", TimeSlot.fromString("08:30 - 18:00"))
        day1.addAppointment(app1)
        self.assertEqual(day1.freeTimeInMinutes(), 270, "Free Time is incorrect after BONUS-Appointment")

    def test_freeTimeSlots(self):
        pass # TBD