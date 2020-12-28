from datetime import timedelta
from customtime import Time
from comparable import Comparable
import util

class TimeSlot(Comparable):
    @staticmethod
    def fromString(timeslotString: str, temporary=False):
        # This is not to be used for reimporting (as the __repr__ produces a different string)
        # The only intended use for this method is to create a timeslot easily from a string literal, i.e. for testing
        # fromDict should be used for imports
        start, end = timeslotString.split(" - ", 1)
        return TimeSlot(util.timeParse(start), util.timeParse(end), temporary=temporary)

    @staticmethod
    def fromDict(valueDict: dict, temporary=False):
        startTimeString = valueDict['startTime']
        endTimeString = valueDict['endTime']
        return TimeSlot(util.timeParse(startTimeString), util.timeParse(endTimeString), temporary=temporary)

    def __init__(self, start: Time, end: Time, temporary=False):
        self.__start = start
        self.__end = end
        self.task = None # Not persisted
        self.temporary = temporary
        if self.startTime > self.endTime:
            raise ValueError(f"Start date cannot be after the end date! {self.startTime} was before {self.endTime}")
        elif self.startTime == self.endTime:
            raise ValueError(f"Start date cannot be equal to the end date! {self.startTime} was equal to {self.endTime}")
    
    @property
    def startTimeString(self):
        return f"{self.__start.hours:02}:{self.__start.minutes:02}"

    @property
    def startTime(self):
        return self.__start

    @property
    def endTimeString(self):
        return f"{self.__end.hours:02}:{self.__end.minutes:02}"

    @property
    def endTime(self):
        return self.__end

    def timeInMinutes(self) -> int:
        return (self.__end - self.__start).total_minutes()

    @property
    def durationInMinutes(self) -> int:
        return self.timeInMinutes()

    def export(self) -> dict:
        return {
            "startTime" : self.startTimeString,
            "endTime" : self.endTimeString
        }

    def __repr__(self) -> str:
        if self.task is None:
            return f"{self.startTimeString} - {self.endTimeString} <empty>"
        else:
            return f"{self.startTimeString} - {self.endTimeString} ({self.task.name})"

    def __eq__(self, other) -> bool:
        return self.startTime == other.startTime and self.endTime == other.endTime

    def overlaps(self, other) -> bool:
        # Notation: self = [], other = {}

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.startTime <= other.startTime and other.endTime <= self.endTime:
            return True

        # Scenario {[]} (also covers the case where they are EQUAL)
        if other.startTime <= self.startTime and self.endTime <= other.endTime:
            return True

        # Scenario [{]}
        if self.startTime <= other.startTime and other.startTime < self.endTime:
            return True

        # Scenario {[}]
        if other.startTime <= self.startTime and self.startTime < other.endTime:
            return True

        # If no scenario matches
        return False

    def nonOverlap(self, other) -> []: # Return new TimeSlot(s) that show the time of SELF that does NOT overlap with the other timeSlot
        # Notation: self = [], other = {}
        # ONLY the time portion WITHIN [] that does not overlap is counted! Non-overlaps from {} are obviously discarded!
        # ORDER OF SCENARIOS MATTERS

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.startTime <= other.startTime and other.endTime <= self.endTime:
            lst = []
            if self.startTime != other.startTime: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(self.startTime, other.startTime))
            if self.endTime != other.endTime: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(other.endTime, self.endTime))
            return lst

        # Scenario {[]}
        if other.startTime <= self.startTime and self.endTime <= other.endTime:
            return []

        # Scenario [{]}
        if self.startTime <= other.startTime and other.startTime < self.endTime:
            lst = []
            if self.startTime != other.startTime: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(self.startTime, other.startTime))
            return lst

        # Scenario {[}]
        if other.startTime <= self.startTime and self.startTime < other.endTime:
            lst = []
            if other.endTime != self.endTime: # Extra check to avoid 0 minute TimeSlots in case of equal boundaries
                lst.append(TimeSlot(other.endTime, self.endTime))
            return lst



        # If no scenario matches
        return [self.copy()] # Generate new, identical object (except the task-reference, which is not copied)

    def copy(self): # The task-reference is NOT COPIED
        return TimeSlot.fromDict(self.export())