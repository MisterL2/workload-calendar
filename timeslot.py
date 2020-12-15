from datetime import timedelta
from customtime import Time
from base import Base
import util

class TimeSlot(Base):
    @staticmethod
    def fromString(timeslotString: str):
        start, end = timeslotString.split(" - ")
        return TimeSlot(util.timeParse(start), util.timeParse(end))

    def __init__(self, start: Time, end: Time):
        self.__start = start
        self.__end = end
        if self.start >= self.end:
            raise Exception(f"Start date cannot be after the end date! {self.start} was before {self.end}")
    
    @property
    def start(self):
        return f"{self.__start.hours:02}:{self.__start.minutes:02}"

    @property
    def end(self):
        return f"{self.__end.hours:02}:{self.__end.minutes:02}"

    def timeInMinutes(self) -> int:
        return (self.__end - self.__start).total_minutes()

    def __repr__(self) -> str:
        return f"{self.start} - {self.end}"