from day import Day
from week import Week
from datetime import date
from task import Task
from timeslot import TimeSlot
from customtime import Time
from scheduleexceptions import DateNotFoundException, ImpossibleScheduleException
import arrow
import util

class Schedule():
    @staticmethod
    def fromDict(valueDict: {}, globalTasks: [Task]):
        created, lastWorkConfirmed, scheduleDays = util.dateTimeStringToArrow(valueDict["created"]), util.dateTimeStringToArrow(valueDict["lastWorkConfirmed"]), valueDict["scheduleDays"]
        days = [Day.fromDict(scheduleDayDict, globalTasks=globalTasks) for scheduleDayDict in scheduleDays]
        return Schedule(days, lastWorkConfirmed, created=created)

    def __init__(self, days: [Day], lastWorkConfirmed: arrow.Arrow, created=None):
        self.lastWorkConfirmed = lastWorkConfirmed

        if created is None:
            self.created = arrow.now()
        else:
            self.created = created
        
        self.__days = []

        for day in days: # Deepcopy
            self.addDay(day.copy())

    def days(self):
        return self.__days

    def addHistory(self, days: [Day]): # Adds the history (previous schedule) to the schedule
        self.__days = [day.copy() for day in days] + self.__days

    def addDay(self, day: Day):
        for existingDay in self.__days:
            if existingDay.date == day.date:
                raise Exception(f"Error: Trying to add a day to a Schedule for a date that already exists: {day} -/> {existingDay}")
        self.__days.append(day)

    def getDay(self, date: date) -> Day:
        for day in self.__days:
            if day.date == date:
                return day

        raise DateNotFoundException("No day with this date found!")

    def getWeek(self, anyDateOfThatWeek: date) -> Week:
        if anyDateOfThatWeek < self.__days[0].date: # Before the first day of the schedule, not including today
            raise DateNotFoundException("This week is before the start of the schedule!")
        elif anyDateOfThatWeek > self.__days[-1].date: # After the last day of the schedule
            raise DateNotFoundException("This week is after the end of the schedule!")

        startDate = arrow.get(anyDateOfThatWeek).shift(days=-anyDateOfThatWeek.weekday()).date() # Move backwards to the next monday (no shift is done if anyDateOfThatWeek is a monday)

        if startDate < self.__days[0].date: # If the lower limit is reached, start the week with the first day. In this case, the week doesn't go from monday-sunday but from the first day to sunday
            startDate = self.__days[0].date

        currentWeekday = startDate.weekday() # In most cases this is 7, but if the startDate is mid-week this will have a value
        startIndex = 0
        for i, day in enumerate(self.__days):
            if day.date == startDate:
                startIndex = i
                break

        weekDays = [day.copy() for day in self.__days[startIndex : startIndex + (7 - currentWeekday)]] # All days from startDate to the next sunday

        return Week(weekDays)

    def scheduleTask(self, task: Task, start: arrow.Arrow, minutes=None, debug=False):
        # TODO: Consider minBlock
        
        if minutes is None:
            minutesToSchedule = task.maxRemainingTime
        else:
            minutesToSchedule = minutes


        if debug:
            print(f"Schedule is scheduling {minutesToSchedule}min for task {task}")

        scheduledMinutes = 0

        startTime = util.arrowToTime(start)

        for day in self.__days:
            if debug:
                print("\n")
                print(day, end=" -> ")
            if task.maxRemainingTime == 0 or minutesToSchedule == scheduledMinutes:
                if debug: print("A", end="")
                return

            # Skip days prior to the startDate
            if day.date < start.date():
                if debug: print("B", end="")
                continue

            # For the start day, consider only the times that lie after the start time
            if day.date == start.date():
                if debug: print("C", end="")
                freeTimeSlots = day.freeTimeSlots(after=startTime)

            # Days in the future
            if day.date > start.date():
                if debug: print("D", end="")
                freeTimeSlots = day.freeTimeSlots()

            if len(freeTimeSlots) == 0:
                if debug: print("E", end="")
                continue

            # For the valid TimeSlots of the future, fill them with the task until they are either all filled or "minutesToSchedule" minutes are scheduled
            for ts in freeTimeSlots:
                if debug: print("F", end="")

                if task.maxRemainingTime == 0 or minutesToSchedule == scheduledMinutes:
                    if debug: print("G", end="")
                    return

                # If TimeSlot is <= to what still needs to be scheduled, fill it completely
                if ts.durationInMinutes <= (minutesToSchedule - scheduledMinutes):
                    if debug: print("H", end="")
                    # Schedule the Task
                    day.scheduleTask(ts, task, debug=debug)

                    # Update the counters
                    task.addCompletionTime(ts.durationInMinutes) # This mutates the ORIGINAL TASK
                    scheduledMinutes += ts.durationInMinutes

                else: # If TimeSlot is bigger than what needs to be scheduled, fill the first section of it (until "minutesToSchedule" minutes are scheduled)
                    if debug: print("I", end="")
                    # Build the Partial TimeSlot
                    remainingMinutesToSchedule = minutesToSchedule - scheduledMinutes
                    length = Time.fromMinutes(remainingMinutesToSchedule)
                    partialTimeSlot = TimeSlot(ts.startTime, ts.startTime + length)

                    # Schedule the Task
                    day.scheduleTask(partialTimeSlot, task, debug=debug)

                    # Update the counters
                    task.addCompletionTime(partialTimeSlot.durationInMinutes) # This mutates the ORIGINAL TASK
                    scheduledMinutes += partialTimeSlot.durationInMinutes # Unnecessary. ScheduledMinutes will == MinutesToSchedule after this every time.
                    return # Since the TimeSlot was bigger than the remaining minutesToSchedule, we are done here now.
        raise ImpossibleScheduleException("Unable to schedule task!")


    def __repr__(self) -> str:
        return f"Schedule ({util.formatDate(self.__days[0].date, time=False)} - {util.formatDate(self.__days[-1].date, time=False)}\n" + "\n".join([repr(day) for day in self.__days])

    def export(self) -> {}:
        return {
            "scheduleDays" : [day.export(forSchedule=True) for day in self.__days],
            "created" : util.formatDate(self.created), # The schedule is built anew whenever requested, so this will be updated
            "lastWorkConfirmed" : util.formatDate(self.lastWorkConfirmed) # This is a pointer to the last time that the user confirmed a work block. Users should be prompted to confirm past work blocks when initialising the schedule
        }

    def recentlyCompleted(self) -> []:
        recentlyCompleted = []
        currentArrow = arrow.now()
        affectedDays = list(filter(lambda day : day.date >= self.lastWorkConfirmed.date() and day.date <= currentArrow.date(), self.__days))
        for affectedDay in affectedDays:
            timeSlots = [ts for ts in affectedDay.timeSlots if ts.taskOrAppointment is not None]
            if affectedDay.date == self.lastWorkConfirmed.date(): # First day of area
                timeSlots = list(filter(lambda ts: ts.endTime > Time(self.lastWorkConfirmed.hour, self.lastWorkConfirmed.minute), timeSlots))
                # Remove all timeslots prior
            if affectedDay.date == currentArrow.date(): # NOT an elif, as a day can be both start and end day
                timeSlots = list(filter(lambda ts: ts.endTime < Time(self.lastWorkConfirmed.hour, self.lastWorkConfirmed.minute), timeSlots))
                # Remove all timeslot after
            for timeSlot in timeSlots:
                recentlyCompleted.append({"dateString" : util.dateString(affectedDay.date), "timeSlot" : timeSlot, "task" : timeSlot.taskOrAppointment})
        return recentlyCompleted