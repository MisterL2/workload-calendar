from timeslot import TimeSlot

class Appointment():
    @staticmethod
    def fromDict(valueDict: dict):
        name = valueDict["name"]
        task = valueDict["task"]
        timeSlot = TimeSlot.fromDict(valueDict["timeSlot"])
        return Appointment(name, timeSlot, task=task)

    def __init__(self, name: str, timeSlot: TimeSlot, task=None):
        self.task = task # If the appointment belong to a task
        self.name = name
        self.timeSlot = timeSlot
        if task is not None:
            self.timeSlot.task = task
        else:
            self.timeSlot.task = self # Infinite recursion

    def overlaps(self, other) -> bool:
        return self.timeSlot.overlaps(other.timeSlot)

    def export(self) -> dict:
        return {
            "task" : self.task, # TODO - So far only supports "None" for task. Building persistence / loading for tasks could be tricky. Needs to use uuid reference rather than task copy to avoid going out of sync.
            "name" : self.name,
            "timeSlot" : self.timeSlot.export()
        }

    def __eq__(self, other) -> bool:
        return self.task == other.task and self.name == other.name and self.timeSlot == other.timeSlot

    def __repr__(self) -> str:
        if self.task is not None:
            return f"{self.name} ({self.timeSlot.timeString}) [{self.task}]"
        else:
            return f"{self.name} ({self.timeSlot.timeString})"