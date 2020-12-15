from datetime import *
import util
from timeslot import TimeSlot
from base import Base

class Day(Base):
    @staticmethod
    def fromDict(valueDict: dict):
        parsedDate = util.dateStringToArrow(valueDict["dateString"]).date()
        timeslots = [TimeSlot.fromString(t) for t in valueDict["timeslots"]]
        return Day(parsedDate, timeslots)

    def __init__(self, date: date, timeslots: [TimeSlot]):
        self.date = date
        self.timeslots = timeslots
    
    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    @property
    def day(self):
        return self.date.day

    @property
    def dateString(self):
        return util.dateString(self.date)

    def timeInMinutes(self) -> int:
        return sum([timeslot.timeInMinutes() for timeslot in self.timeslots])

    def export(self):
        return {
            "dateString" : self.dateString,
            "timeslots" : self.timeslots
            }

    def __repr__(self) -> str:
        timeslotString = "; ".join([t for t in self.timeslots])
        return f"{self.dateString} ({self.timeInMinutes()/60:.1f} h) Timeslots: [{timeslotString}]"

    def __lt__(self, other) -> bool:
        return self.date < other.date

    def __gt__(self, other) -> bool:
        return self.date > other.date
