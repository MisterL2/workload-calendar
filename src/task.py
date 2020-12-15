from arrow import Arrow
import util

class Task:
    @staticmethod
    def fromDict(valueDict: dict):
        deadlineArrow = util.dateTimeStringToArrow(valueDict["deadline"])
        return Task(valueDict["name"], valueDict["timeRequirement"], valueDict["priority"], deadlineArrow, valueDict["minBlock"])

    def __init__(self, name: str, timeRequirement: int, priority: int, deadline: Arrow, minBlock: int):
        self.__deadlineArrow = deadline
        self.__data = {
            "name" : name,
            "timeRequirement" : timeRequirement, # In Minutes
            "priority" : priority,
            "deadline" : util.dateString(deadline, time=True),
            "minBlock" : minBlock  # If this is 120, it means that this task should not be split up into chunks smaller than 120mins.
        }

    def updateValue(self,key,value):
        self.__data[key] = value

    @property
    def name(self):
        return self.__data["name"]

    @property
    def timeRequirement(self):
        return self.__data["timeRequirement"]

    @property
    def priority(self):
        return self.__data["priority"]

    @property
    def deadline(self) -> Arrow:
        return self.__deadlineArrow

    @property
    def deadlineString(self) -> str:
        return self.__data["deadline"]

    @property
    def minBlock(self):
        return self.__data["minBlock"]

    def export(self):
        return self.__data

    def fitsIn(self, timeslot):
        return timeslot.timeInMinutes() >= self.minBlock

    def __repr__(self):
        return f"{self.name} ({round(self.timeRequirement/60,1)} h) Priority: {self.priority}/10 Deadline: [{self.deadline}] Min Block Size: {self.minBlock} min"