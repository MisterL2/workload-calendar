from timeslot import TimeSlot

class Appointment():
    @staticmethod
    def fromDict(valueDict: dict):
        name = valueDict["name"]
        timeSlot = TimeSlot.fromDict(valueDict["timeSlot"])
        return Appointment(name, timeSlot)

    def __init__(self, name: str, timeSlot: TimeSlot):
        self.name = name
        self.timeSlot = timeSlot

    def overlaps(self, other) -> bool:
        return self.timeSlot.overlaps(other.timeSlot)

    def export(self) -> dict:
        return {
            "name" : self.name,
            "timeSlot" : self.timeSlot.export()
        }

    def __repr__(self) -> str:
        return f"Appointment[name='{self.name}', timeSlot='{self.timeSlot}'"