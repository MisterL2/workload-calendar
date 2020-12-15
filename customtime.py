from base import Base

class Time(Base):
    def __init__(self, hours: int, minutes: int):
        if hours > 23 or minutes > 59:
            raise Exception(f"Invalid Time: {hours:02} h {minutes:02} min")
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

    def __repr__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}"

