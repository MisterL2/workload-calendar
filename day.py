from datetime import *
import util
from timeslot import TimeSlot
from base import Base

class Day(Base):
    def __init__(self, dayDate: date, timeslots: [TimeSlot]):
        self.__dayDate = dayDate
        self.timeslots = timeslots
    
    @property
    def dayDate(self):
        return util.dateString(self.__dayDate)

    def timeInMinutes(self) -> int:
        return sum([timeslot.timeInMinutes() for timeslot in self.timeslots])

    def export(self):
        return {
            "dayDate" : self.dayDate,
            "timeslots" : self.timeslots
            }

    def __repr__(self) -> str:
        timeslotString = "; ".join([t for t in self.timeslots])
        return f"{self.dayDate} ({self.timeInMinutes()/60:.1f} h) Timeslots: [{timeslotString}]"

    def __lt__(self, other) -> bool:
        return self.__dayDate < other.__dayDate

    def __gt__(self, other) -> bool:
        return self.__dayDate > other.__dayDate
