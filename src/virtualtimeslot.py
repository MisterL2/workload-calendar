from timeslot import TimeSlot
from task import Task

class VirtualTimeSlot():
    def __init__(self, timeSlot: TimeSlot, task: Task):
        self.__timeSlot = timeSlot
        self.__task = task

    def __repr__(self) -> str:
        return f"{self.__timeSlot} ({self.__task.name})"

    def timeInMinutes(self) -> int:
        return self.__timeSlot.timeInMinutes()