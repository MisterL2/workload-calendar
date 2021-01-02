from arrow import Arrow
from typing import Union
import uuid
import util

class Task:
    @staticmethod
    def fromRecurring(recurringTask, deadline: Arrow):
        # Use recurring Task as base
        task = Task.fromDict(recurringTask.export())
        # Generate fresh UUID
        task.updateValue("uuid", util.generateUUID())
        # Apply deadline
        task.updateValue("deadline", deadline)
        return task

    @staticmethod
    def fromDict(valueDict: dict):
        deadlineArrow = util.dateTimeStringToArrow(valueDict["deadline"])
        return Task(valueDict["uuid"], valueDict["name"], valueDict["minTime"], valueDict["maxTime"], valueDict["priority"], deadlineArrow, valueDict["minBlock"], completedTime=valueDict["completedTime"], recurringTaskUUID=valueDict["recurringTaskUUID"], start=valueDict["start"])

    def __init__(self, uuidString: str, name: str, minTimeMinutes: int, maxTimeMinutes: int, priority: int, deadline: Arrow, minBlock: int, completedTime: int=0, recurringTaskUUID=None, start=None):
        self.__deadlineArrow = deadline if deadline is not None else util.getInfinityDate()
        self.__start = util.dateStringToArrow(start) if start is not None else util.smoothCurrentArrow()
        self.__data = {
            "recurringTaskUUID" : recurringTaskUUID, # If this task was generated from a recurring task, keep that ID as reference so they can all be added / removed as appropriate
            "uuid": uuidString,
            "name" : name,
            "completedTime" : completedTime,
            "minTime" : int(minTimeMinutes), # In Minutes
            "maxTime" : int(maxTimeMinutes), # In Minutes
            "priority" : priority,
            "deadline" : util.dateString(self.__deadlineArrow, time=True),
            "start" : util.dateString(self.__start, time=True),
            "minBlock" : minBlock  # If this is 120, it means that this task should not be split up into chunks smaller than 120mins.
        }

    def updateValue(self, key, value):
        if key == "deadline": # As arrow
            if value is None:
                value = util.getInfinityDate()
            self.__deadlineArrow = value # Also change the internal field to remain consistent
            value = util.dateString(value, time=True)
        
        if key == "start": # As arrow
            self.__start = value # Also change the internal field to remain consistent
            value = util.dateString(value, time=True)

        self.__data[key] = value

    def addTimeRequirement(self, minutesToAdd: int): # Make the task longer
        self.updateValue("minTime", minutesToAdd + self.minTime)
        self.updateValue("maxTime", minutesToAdd + self.maxTime)

    def addCompletionTime(self, minutesToAdd: int) -> int: # Increase progress. Returns an int to reflect state: 0 = not finished, 1 = minimum time reached, 2 = maximum time reached
        self.updateValue("completedTime", int(minutesToAdd + self.completedTime))

        return int(self.completedTime > self.minTime) + int(self.completedTime > self.maxTime)
        # 0 = not finished
        # 1 = minimum time reached
        # 2 = maximum time reached

    @property
    def recurringTaskUUID(self) -> str:
        return self.__data["recurringTaskUUID"]

    @property
    def start(self) -> Arrow:
        return self.__start

    @property
    def uuid(self) -> str:
        return self.__data["uuid"]

    @property
    def uuidInt(self) -> int:
        return uuid.UUID(str(self.uuid)).int

    @property
    def name(self) -> str:
        return self.__data["name"]

    @property
    def minTime(self) -> int: # In Minutes
        return self.__data["minTime"]
    
    @property
    def maxTime(self) -> int: # In Minutes
        return self.__data["maxTime"]

    @property
    def avgTime(self) -> int:
        return (self.minTime + self.maxTime) // 2

    @property
    def priority(self) -> float:
        return self.__data["priority"]

    @property
    def deadline(self) -> Arrow:
        return self.__deadlineArrow

    @property
    def deadlineString(self) -> str:
        return self.__data["deadline"]

    @property
    def minBlock(self) -> int:
        return self.__data["minBlock"]

    @property
    def completedTime(self) -> int:
        return self.__data["completedTime"]

    @property
    def minRemainingTime(self) -> int:
        return max(0, self.minTime - self.__data["completedTime"]) # At least 0, even if minTime has already been passed

    @property
    def maxRemainingTime(self):
        return self.maxTime - self.__data["completedTime"]

    @property
    def avgRemainingTime(self):
        return max(0, self.avgTime - self.__data["completedTime"]) # At least 0, even if minTime has already been passed

    @property
    def progress(self):
        return self.completedTime / self.maxTime # For consistency reasons, use maxTime

    @property
    def progressPercentage(self):
        return f"{round(self.progress*100)}%"

    def hasDeadline(self) -> bool:
        return self.deadline != util.getInfinityDate()

    def export(self):
        return self.__data

    def fitsIn(self, timeslot):
        return timeslot.timeInMinutes() >= self.minBlock

    def displayRecurringTask(self) -> str:
        return f"{self.name} ({round(self.maxTime/60,1)} h) [Prio: {self.priority}] Progress: {self.progressPercentage}"

    def __repr__(self) -> str:
        if self.hasDeadline():
            return f"{self.name} ({round(self.maxTime/60,1)} h) [Prio: {self.priority}] Deadline: {util.formatDate(self.deadline)} Progress: {self.progressPercentage}"
        else:
            return f"{self.name} ({round(self.maxTime/60,1)} h) [Prio: {self.priority}] Deadline: <None> Progress: {self.progressPercentage}"
        #return f"{self.name} ({round(self.minTime/60,1)} h - {round(self.maxTime/60,1)} h) Priority: {self.priority}/10 Deadline: [{self.deadline}] Min Block Size: {self.minBlock} min"

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return self.uuidInt

    def copy(self):
        return Task.fromDict(self.export())
