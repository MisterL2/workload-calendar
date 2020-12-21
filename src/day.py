from datetime import date
import util
from timeslot import TimeSlot
from comparable import Comparable
from appointment import Appointment

class Day(Comparable):
    @staticmethod
    def fromDict(valueDict: dict):
        parsedDate = util.dateStringToArrow(valueDict["dateString"]).date()
        timeSlots = [TimeSlot.fromDict(t) for t in valueDict["timeSlots"]]
        appointments = [Appointment.fromDict(appDict) for appDict in valueDict["appointments"]]
        return Day(parsedDate, timeSlots, appointments)

    def __init__(self, date: date, timeSlots: [TimeSlot], appointments: [Appointment]):
        self.date = date
        self.timeSlots = timeSlots
        self.appointments = appointments
    
    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    @property
    def day(self):
        return self.date.day

    @property
    def dateString(self):
        return util.dateString(self.date)

    def timeInMinutes(self) -> int:
        return sum([timeSlot.timeInMinutes() for timeSlot in self.timeSlots])

    def addAppointment(self, appointment: Appointment):
        # Warn user if this overlaps another appointment, but accept it (overlapping appointments are valid)
        for existingAppointment in self.appointments:
            if existingAppointment.overlaps(appointment):
                print(f"WARNING: Added appointment overlaps with '{existingAppointment}'")

        self.appointments.append(appointment)

    def export(self) -> dict:
        return {
            "dateString" : self.dateString,
            "timeSlots" : [ts.export() for ts in self.timeSlots],
            "appointments" : [app.export() for app in self.appointments]
            }

    def __repr__(self) -> str:
        timeSlotString = "; ".join([t for t in self.timeSlots])
        appointmentString = "; ".join([repr(a) for a in self.appointments])
        return f"{self.dateString} ({self.timeInMinutes()/60:.1f} h) Timeslots: [{timeSlotString}] Appointments: [{appointmentString}]"

    def __lt__(self, other) -> bool:
        return self.date < other.date

    def __gt__(self, other) -> bool:
        return self.date > other.date
