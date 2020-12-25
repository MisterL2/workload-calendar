from arrow import Arrow
import util

class Task:
    @staticmethod
    def fromDict(valueDict: dict):
        deadlineArrow = util.dateTimeStringToArrow(valueDict["deadline"])
        return Task(valueDict["name"], valueDict["minTime"], valueDict["maxTime"], valueDict["priority"], deadlineArrow, valueDict["minBlock"])

    def __init__(self, name: str, minTime: int, maxTime: int, priority: int, deadline: Arrow, minBlock: int):
        self.__deadlineArrow = deadline
        self.__data = {
            "name" : name,
            "completedTime" : 0,
            "minTime" : minTime, # In Minutes
            "maxTime" : maxTime, # In Minutes
            "priority" : priority,
            "deadline" : util.dateString(deadline, time=True),
            "minBlock" : minBlock  # If this is 120, it means that this task should not be split up into chunks smaller than 120mins.
        }

    def updateValue(self, key, value):
        self.__data[key] = value

    def addTaskTime(self, timeToAdd: int): # In Minutes
        self.updateValue("minTime", timeToAdd + self.minTime)
        self.updateValue("maxTime", timeToAdd + self.maxTime)

    def addCompletionTime(self, timeToAdd: int): # In Minutes
        self.updateValue("completedTime", timeToAdd + self.completedTime)
        if self.completedTime > self.maxTime:
            print("Exceeded MAXIMUM time, is the task finished? [Ask user for yes/no here]")
        elif self.completedTime > self.minTime:
            print("Exceeded minimum time, is the task finished? [Ask user for yes/no here]")

    @property
    def name(self) -> str:
        return self.__data["name"]

    @property
    def minTime(self) -> int:
        return self.__data["minTime"]
    
    @property
    def maxTime(self) -> int:
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

    def export(self):
        return self.__data

    def fitsIn(self, timeslot):
        return timeslot.timeInMinutes() >= self.minBlock

    def __repr__(self):
        return f"{self.name} ({round(self.minTime/60,1)} - {round(self.maxTime/60,1)} h) Priority: {self.priority}/10 Deadline: [{self.deadline}] Min Block Size: {self.minBlock} min"