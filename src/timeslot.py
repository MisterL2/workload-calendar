from datetime import timedelta
from customtime import Time
from comparable import Comparable
import util

class TimeSlot(Comparable):
    @staticmethod
    def fromString(timeslotString: str):
        start, end = timeslotString.split(" - ")
        return TimeSlot(util.timeParse(start), util.timeParse(end))

    @staticmethod
    def fromDict(valueDict: dict):
        startTimeString = valueDict['startTime']
        endTimeString = valueDict['endTime']
        return TimeSlot(util.timeParse(startTimeString), util.timeParse(endTimeString))

    def __init__(self, start: Time, end: Time):
        self.__start = start
        self.__end = end
        if self.start >= self.end:
            raise ValueError(f"Start date cannot be after the end date! {self.start} was before {self.end}")
    
    @property
    def start(self):
        return f"{self.__start.hours:02}:{self.__start.minutes:02}"

    @property
    def end(self):
        return f"{self.__end.hours:02}:{self.__end.minutes:02}"

    def timeInMinutes(self) -> int:
        return (self.__end - self.__start).total_minutes()

    def export(self) -> dict:
        return {
            "startTime" : self.start,
            "endTime" : self.end
        }

    def __repr__(self) -> str:
        return f"{self.start} - {self.end}"

    def __eq__(self, other) -> bool:
        return self.start == other.start and self.end == other.end

    def overlaps(self, other) -> bool:
        # Notation: self = [], other = {}
        # ORDER OF SCENARIOS MATTERS

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.start <= other.start and other.end <= self.end: return True

        # Scenario {[]}
        if other.start <= self.start and self.end <= other.end: return True

        # Scenario [{]}
        if self.start <= other.start and other.start <= self.end: return True

        # Scenario {[}]
        if other.start <= self.start and self.start <= other.end: return True

        # If no scenario matches
        return False

    def nonOverlap(self, other) -> []: # Return new TimeSlot(s) that show the time of SELF that does NOT overlap with the other timeSlot
        # Notation: self = [], other = {}
        # ONLY the time portion WITHIN [] that does not overlap is counted! Non-overlaps from {} are obviously discarded!
        # ORDER OF SCENARIOS MATTERS

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.start <= other.start and other.end <= self.end:
            lst = []
            if self.start != other.start: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(self.__start, other.__start))
            if self.end != other.end: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(other.__end, self.__end))
            return lst

        # Scenario {[]}
        if other.start <= self.start and self.end <= other.end:
            return []

        # Scenario [{]}
        if self.start <= other.start and other.start <= self.end:
            lst = []
            if self.start != other.start: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(self.__start, other.__start))
            return lst

        # Scenario {[}]
        if other.start <= self.start and self.start <= other.end:
            lst = []
            if other.end != self.end: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(other.__end, self.__end))
            return lst



        # If no scenario matches
        return [TimeSlot.fromString(repr(self))] # Generate new, identical object

    def copy(self):
        return TimeSlot.fromString(repr(self))