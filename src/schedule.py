from virtualday import VirtualDay
from week import Week
from datetime import date


class Schedule():
    def __init__(self, virtualDays: [VirtualDay]):
        self.virtualDays = virtualDays

    def getVirtualDay(self, date: date) -> VirtualDay:
        pass

    def getWeek(self, anyDateOfThatWeek: date) -> Week:
        # If the date is in the past (make sure NOT to exclude 00:00h on TODAY), move forward till you find a day that isn't.
        # If the date is not a monday, go back till you find a monday. That is the startdate.
        # If, while going back, you meet the current date/time, stop there and only display the week partially, starting from that date.
        pass