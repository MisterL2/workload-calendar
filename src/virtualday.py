from datetime import date
from virtualtimeslot import VirtualTimeSlot
from customtime import Time

class VirtualDay():
    def __init__(self, date: date, virtualTimeSlots: [VirtualTimeSlot]):
        self.date = date
        self.virtualTimeSlots = virtualTimeSlots

    def workTimeInMinutes(self) -> int:
        return sum([vts.timeInMinutes() for vts in self.virtualTimeSlots])

    def dayHeadline(self) -> str:
        return f"{self.weekdayString} ({self.date}) - {(self.workTimeInMinutes/60):.1} h"

    def virtualTimeSlotRepr(self) -> str:
        return "\n".join([repr(vts) for vts in self.virtualTimeSlots])

    def weekdayString(self) -> str:
        return self.date.strftime("%A")

    def __repr__(self) -> str:
        return self.dayHeadline() + "\n" + self.virtualTimeSlotRepr()