from arrow import Arrow
from typing import Union
import uuid
import util

class Task:
    @staticmethod
    def fromDict(valueDict: dict):
        deadlineArrow = util.dateTimeStringToArrow(valueDict["deadline"])
        return Task(valueDict["uuid"], valueDict["name"], valueDict["minTime"], valueDict["maxTime"], valueDict["priority"], deadlineArrow, valueDict["minBlock"], completedTime=valueDict["completedTime"])

    def __init__(self, uuid: str, name: str, minTimeMinutes: int, maxTimeMinutes: int, priority: int, deadline: Arrow, minBlock: int, completedTime: int=0):
        self.__deadlineArrow = deadline
        self.__data = {
            "uuid": uuid,
            "name" : name,
            "completedTime" : completedTime,
            "minTime" : minTimeMinutes, # In Minutes
            "maxTime" : maxTimeMinutes, # In Minutes
            "priority" : priority,
            "deadline" : util.dateString(deadline, time=True) if deadline is not None else None,
            "minBlock" : minBlock  # If this is 120, it means that this task should not be split up into chunks smaller than 120mins.
        }

    def updateValue(self, key, value):
        self.__data[key] = value

    def addTimeRequirement(self, minutesToAdd: int): # Make the task longer
        self.updateValue("minTime", minutesToAdd + self.minTime)
        self.updateValue("maxTime", minutesToAdd + self.maxTime)

    def addCompletionTime(self, minutesToAdd: int, showUserPrompt=False): # Increase progress
        self.updateValue("completedTime", int(minutesToAdd + self.completedTime))
        if showUserPrompt:
            if self.completedTime > self.maxTime:
                print("Exceeded MAXIMUM time, is the task finished? [Ask user for yes/no here]")
            elif self.completedTime > self.minTime:
                print("Exceeded minimum time, is the task finished? [Ask user for yes/no here]")

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
        return self.deadline is not None

    def export(self):
        return self.__data

    def fitsIn(self, timeslot):
        return timeslot.timeInMinutes() >= self.minBlock

    def __repr__(self) -> str:
        return f"{self.name} ({round(self.maxTime/60,1)} h) [Prio: {self.priority}] Deadline: {util.formatDate(self.deadline)} Progress: {self.progressPercentage}"
        #return f"{self.name} ({round(self.minTime/60,1)} h - {round(self.maxTime/60,1)} h) Priority: {self.priority}/10 Deadline: [{self.deadline}] Min Block Size: {self.minBlock} min"

    def __eq__(self, other) -> bool:
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return self.uuidInt

    def copy(self):
        return Task.fromDict(self.export())
