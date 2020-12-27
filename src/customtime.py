from comparable import Comparable

class Time(Comparable):
    @staticmethod
    def fromMinutes(minutes: int):
        return Time(minutes // 60, minutes % 60)

    @staticmethod
    def fromString(timeString: str):
        hours = int(timeString.split(":")[0])
        minutes = int(timeString.split(":")[1])
        return Time(hours, minutes)

    def __init__(self, hours: int, minutes: int):
        if hours > 23 or minutes > 59:
            raise ValueError(f"Invalid Time: {hours:02} h {minutes:02} min")
        self.hours = hours
        self.minutes = minutes

    def total_minutes(self):
        return self.hours*60 + self.minutes

    def __gt__(self, other):
        return self.hours > other.hours or (self.hours == other.hours and self.minutes > other.minutes)
    
    def __lt__(self, other):
        return self.hours < other.hours or (self.hours == other.hours and self.minutes < other.minutes)

    def __eq__(self, other):
        return self.hours == other.hours and self.minutes == other.minutes

    def __sub__(self, other):
        if self < other:
            raise Exception("Invalid subtraction! Second value is too large!")
        minutes = self.minutes - other.minutes
        hours = self.hours - other.hours
        if minutes < 0:
            minutes += 60
            hours -= 1
        return Time(hours, minutes)

    def __add__(self, other):
        minutes = self.minutes + other.minutes
        hours = self.hours + other.hours
        if minutes > 59:
            minutes -= 60
            hours += 1
        return Time(hours, minutes)

    def export(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}"

