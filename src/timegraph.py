from typing import Tuple


class TimeInterval():
    def __init__(self, name: str, startTimeInMinutes: int, endTimeInMinutes: int):
        self.name = name
        self.startTimeInMinutes = startTimeInMinutes
        self.endTimeInMinutes = endTimeInMinutes

    @property
    def durationInMinutes(self):
        return self.endTimeInMinutes - self.startTimeInMinutes

    def overlapsEnd(self, other): # If our start is inside another (previous) time interval -> shift the other one to an earlier point
        # Notation: self = [], other = {}

        # Scenario {[]}  (also covers the case where they are EQUAL)
        if other.startTimeInMinutes <= self.startTimeInMinutes and self.endTimeInMinutes <= other.endTimeInMinutes:
            return True

        # Scenario {[}]
        if other.startTimeInMinutes <= self.startTimeInMinutes and self.startTimeInMinutes < other.endTimeInMinutes:
            return True

        return False

    def overlapsStart(self, other): # If our end is inside another (later) time interval -> shift us to an earlier point
        # Notation: self = [], other = {}

        # Scenario [{}] (also covers the case where they are EQUAL)
        if self.startTimeInMinutes <= other.startTimeInMinutes and other.endTimeInMinutes <= self.endTimeInMinutes:
            return True

        # Scenario [{]}
        if self.startTimeInMinutes <= other.startTimeInMinutes and other.startTimeInMinutes < self.endTimeInMinutes:
            return True

        return False

    def __repr__(self) -> str:
        return f"{self.startTimeInMinutes} ({self.name}) {self.endTimeInMinutes}"
        #return f"{self.startTimeInMinutes/60:.1} ({self.name}) {self.endTimeInMinutes/60:.1}"

class TimeGraph():
    def __init__(self):
        self.timeIntervals = [] # Always sorted

    def addTimeInterval(self, name: str, endTimeInMinutes: int, durationInMinutes: int):
        availableSpace = self.freeSpaceBefore(endTimeInMinutes)
        if availableSpace < durationInMinutes:
            raise Exception(f"Not enough space available to meet all deadlines (not a happy schedule). Needed {durationInMinutes}min but only had {availableSpace}min")

        # Overlapping time intervals are not allowed, so in case of conflict, shift forward
        startTimeInMinutes = endTimeInMinutes - durationInMinutes

        
        newTimeInterval = TimeInterval(name, startTimeInMinutes, endTimeInMinutes)
        
        # First, see if we overlap the START of another TimeInterval
        for existingTimeInterval in self.timeIntervals:
            
            if newTimeInterval.overlapsStart(existingTimeInterval):
                if newTimeInterval.endTimeInMinutes <= existingTimeInterval.endTimeInMinutes:
                    # WE need to be shifted to an earlier point

                    # Abort current insertion attempt and try a new attempt, where the endTime of the TimeInterval to be inserted is equal to the start time of the overlapping previous task.
                    # This effectively shifts the TimeInterval to the closest earlier point
                    # Restart the addTimeInterval process with *different* parameters
                    return self.addTimeInterval(name, existingTimeInterval.startTimeInMinutes, durationInMinutes)
                else:
                    # THEY need to be shifted to an earlier point

                    # Remove the conflicting TimeInterval
                    self.timeIntervals.remove(existingTimeInterval)
                    # Re-add the conflicting TimeInterval with adjusted times (may trigger a recursive cascade of shifting TimeIntervals forward until everything matches)
                    self.addTimeInterval(existingTimeInterval.name, newTimeInterval.startTimeInMinutes, existingTimeInterval.durationInMinutes)
                    # Restart the addTimeInterval process with the *same* parameters (in order to avoid ConcurrentModificationExceptions)
                    return self.addTimeInterval(name, endTimeInMinutes, durationInMinutes)

        # Second, see if we overlap the END of another TimeInterval
        for existingTimeInterval in self.timeIntervals:
            if newTimeInterval.overlapsEnd(existingTimeInterval): # THEY need to be shifted to an earlier point
                if newTimeInterval.endTimeInMinutes <= existingTimeInterval.endTimeInMinutes:
                    # WE need to be shifted to an earlier point

                    # Abort current insertion attempt and try a new attempt, where the endTime of the TimeInterval to be inserted is equal to the start time of the overlapping previous task.
                    # This effectively shifts the TimeInterval to the closest earlier point
                    # Restart the addTimeInterval process with *different* parameters
                    return self.addTimeInterval(name, existingTimeInterval.startTimeInMinutes, durationInMinutes)
                else:
                    # THEY need to be shifted to an earlier point

                    # Remove the conflicting TimeInterval
                    self.timeIntervals.remove(existingTimeInterval)
                    # Re-add the conflicting TimeInterval with adjusted times (may trigger a recursive cascade of shifting TimeIntervals forward until everything matches)
                    self.addTimeInterval(existingTimeInterval.name, newTimeInterval.startTimeInMinutes, existingTimeInterval.durationInMinutes)
                    # Restart the addTimeInterval process with the *same* parameters (in order to avoid ConcurrentModificationExceptions)
                    return self.addTimeInterval(name, endTimeInMinutes, durationInMinutes)
                

        # Add our TimeInterval, now that there is time for it
        self.timeIntervals.append(newTimeInterval)

        self.timeIntervals = sorted(self.timeIntervals, key=lambda ti: ti.startTimeInMinutes)

    def freeSpaceBefore(self, targetTimeInMinutes: int):
        relevantTimeIntervals = filter(lambda ti: ti.startTimeInMinutes < targetTimeInMinutes, self.timeIntervals)
        blockedTimeAmount = 0
        for rti in relevantTimeIntervals:
            # Use duration unless the targetTime is within the TimeInterval; then select only the time from start to targetTime
            blockedTimeAmount += min(rti.durationInMinutes, targetTimeInMinutes - rti.startTimeInMinutes)

        return targetTimeInMinutes - blockedTimeAmount

    def __repr__(self) -> str:
        return " | ".join([repr(ti) for ti in self.timeIntervals])


tg = TimeGraph()
tg.addTimeInterval("first", 500, 300) # 200 - 500
tg.addTimeInterval("last", 1500, 800) # 700 - 1500
tg.addTimeInterval("second", 1200, 300) # 900 - 1200