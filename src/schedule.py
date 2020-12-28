from day import Day
from week import Week
from datetime import date
from task import Task
import util

class Schedule():
    def __init__(self, days: [Day]):
        self.__days = [day.copy() for day in days] # Deepcopy

    def addDay(self, day: Day):
        for existingDay in self.__days:
            if existingDay.date == day.date:
                raise Exception(f"Error: Trying to add a day to a Schedule for a date that already exists: {day} -/> {existingDay}")
        self.__days.append(day)

    def getDay(self, date: date) -> Day:
        for day in self.__days:
            if day.date == date:
                return day

        raise IndexError("No day with this date found!")

    def getWeek(self, anyDateOfThatWeek: date) -> Week:
        # If the date is in the past (make sure NOT to exclude 00:00h on TODAY), move forward till you find a day that isn't.
        # If the date is not a monday, go back till you find a monday. That is the startdate.
        # If, while going back, you meet the current date/time, stop there and only display the week partially, starting from that date.
        pass

    def scheduleTask(self, task: Task, minutes=None):
        # TODO: Consider minBlock

        if minutes is None:
            minutesToSchedule = task.maxRemainingTime
        else:
            minutesToSchedule = minutes

        scheduledMinutes = 0

        currentArrow = util.smoothCurrentArrow()
        currentDate = currentArrow.date()
        currentTime = util.arrowToTime(currentArrow)

        for day in self.__days:
            # Skip days in the past
            if day.date < currentDate:
                continue

            # For the current day, consider only the times that lie in the future
            if day.date == currentDate:
                freeTimeSlots = day.freeTimeSlots(after=currentTime)

            # Days in the future
            if day.date > currentDate:
                freeTimeSlots = day.freeTimeSlots()

            if len(freeTimeSlots) == 0:
                continue

            # For the valid TimeSlots of the future, fill them with the task until they are either all filled or "minutesToSchedule" minutes are scheduled
            for ts in freeTimeSlots:

                # If TimeSlot is smaller than what still needs to be scheduled, fill it completely
                if ts.durationInMinutes < (minutesToSchedule - scheduledMinutes):
                    # Schedule the Task
                    day.scheduleTask(ts, task)

                    # Update the counters
                    task.addCompletionTime(ts.durationInMinutes) # This mutates the ORIGINAL TASK
                    scheduledMinutes += ts.durationInMinutes



            if task.maxRemainingTime == 0 or minutesToSchedule == scheduledMinutes:
                return

        raise Exception("Unable to schedule task!")