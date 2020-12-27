from virtualday import VirtualDay
from virtualweek import VirtualWeek
from datetime import date


class Schedule():
    def __init__(self):
        self.__virtualDays = []

    def addVirtualDay(self, virtualDay: VirtualDay):
        for existingVirtualDay in self.__virtualDays:
            if existingVirtualDay.date == virtualDay.date:
                raise Exception(f"Error: Trying to add a VirtualDay to a Schedule for a date that already exists: {virtualDay} -/> {existingVirtualDay}")
        self.__virtualDays.append(virtualDay)

    def getVirtualDay(self, date: date) -> VirtualDay:
        pass

    def getVirtualWeek(self, anyDateOfThatWeek: date) -> VirtualWeek:
        # If the date is in the past (make sure NOT to exclude 00:00h on TODAY), move forward till you find a day that isn't.
        # If the date is not a monday, go back till you find a monday. That is the startdate.
        # If, while going back, you meet the current date/time, stop there and only display the week partially, starting from that date.
        pass