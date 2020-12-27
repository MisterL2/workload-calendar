from typing import Tuple


class TimeInterval():
    def __init__(self, name: str, startTimeInMinutes: int, endTimeInMinutes: int):
        self.name = name
        self.startTimeInMinutes = startTimeInMinutes
        self.endTimeInMinutes = endTimeInMinutes

    def overlapsEnd(self, other): # If our start is inside another (previous) time interval -> shift the other one to an earlier point
        # Notation: self = [], other = {}

        # Scenario {[]}  (also covers the case where they are EQUAL)
        if other.startTimeInMinutes <= self.startTimeInMinutes and self.endTimeInMinutes <= other.endTimeInMinutes:
            return True

        # Scenario {[}]
        if other.startTimeInMinutes <= self.startTimeInMinutes and self.startTimeInMinutes <= other.endTimeInMinutes:
            return True

        return False

    def overlapsStart(self, other): # If our end is inside another (later) time interval -> shift us to an earlier point
        # Notation: self = [], other = {}

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.startTimeInMinutes <= other.startTimeInMinutes and other.endTimeInMinutes <= self.endTimeInMinutes:
            return True

        # Scenario [{]}
        if self.startTimeInMinutes <= other.startTimeInMinutes and other.startTimeInMinutes <= self.endTimeInMinutes:
            return True

        return False

    def __repr__(self) -> str:
        return f"{self.startTimeInMinutes/60:.1} ({self.name}) {(self.endTimeInMinutes)/60:.1}"

class TimeGraph():
    def __init__(self):
        self.timeIntervals = []

    def addTimeInterval(self, name: str, endTimeInMinutes: int, durationInMinutes: int):
        # Overlapping time intervals are not allowed, so in case of conflict, shift forward
        startTimeInMinutes = endTimeInMinutes - durationInMinutes
        if startTimeInMinutes < 0:
            raise Exception("Start Time is < 0 when adding a time interval -> not a happy schedule")
        
        newTimeInterval = TimeInterval(name, startTimeInMinutes, endTimeInMinutes)
        
        # First, see if WE need to shift
        for existingTimeInterval in self.timeIntervals:
            if newTimeInterval.overlapsStart(existingTimeInterval): # WE need to be shifted to an earlier point
                # Abort current insertion attempt and try a new attempt, where the endTime of the TimeInterval to be inserted is equal to the start time of the overlapping previous task.
                # This effectively shifts the TimeInterval to the closest earlier point
                return self.addTimeInterval(name, existingTimeInterval.startTimeInMinutes, durationInMinutes)

        # Second, see if something else needs to shift
        while True:
            for existingTimeInterval in self.timeIntervals:
                if newTimeInterval.overlapsEnd(existingTimeInterval): # THEY need to be shifted to an earlier point
                    # Remove the conflicting TimeInterval
                    self.timeIntervals.remove(existingTimeInterval)
                    # Re-add the conflicting TimeInterval with adjusted times (may trigger a recursive cascade of shifting TimeIntervals forward until everything matches)
                    self.addTimeInterval(existingTimeInterval.name, newTimeInterval.startTimeInMinutes, existingTimeInterval.durationInMinutes)
                    # Exit the for-loop to avoid concurrentModificationException and go back to the while-loop
                    break
            else: # If there are no more conflicting TimeIntervals
                break # Exit the while-loop

        # Add our TimeInterval, now that there is time for it
        self.timeIntervals.append(newTimeInterval)


#    def __repr__(self) -> str:
#        orderedTimeIntervalStarts = sorted(list(self.timeIntervals.keys()))
#        return "|".join([repr(self.timeIntervals[timeIntervalStart]) for timeIntervalStart in orderedTimeIntervalStarts])

