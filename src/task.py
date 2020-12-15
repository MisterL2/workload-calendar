from arrow import Arrow
import util

class Task:
    def __init__(self, name: str, timeRequirement: int, priority: int, deadline: str, minBlock: int):
        self.__data = {
            "name" : name,
            "timeRequirement" : timeRequirement, # In Minutes
            "priority" : priority,
            "deadline" : deadline,
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
    def deadline(self):
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