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
        isSpecial = valueDict["special"]
        return Day(parsedDate, timeSlots, appointments, special=isSpecial)

    def __init__(self, date: date, timeSlots: [TimeSlot], appointments: [Appointment], special=False): # Remember: don't use mutables as default params
        self.date = date
        self.timeSlots = []
        for timeSlot in timeSlots:
            self.addTimeSlot(timeSlot) # This validates that there are no overlapping timeslots
        self.appointments = appointments
        self.special = special
    
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

    def freeTimeSlots(self) -> [TimeSlot]: # Returns a new list containing new objects / copies
        freeSlots = []
        for timeSlot in self.timeSlots:
            currentTimeSlots = [timeSlot.copy()]
            for appointment in self.appointments:
                newTimeSlots = []
                for currentTimeSlot in currentTimeSlots:
                    newTimeSlots += currentTimeSlot.nonOverlap(appointment.timeSlot)
                currentTimeSlots = newTimeSlots.copy() # .copy() is very important; mutation danger
            freeSlots += currentTimeSlots.copy()
        return freeSlots

    def freeTimeInMinutes(self) -> int: # Later on this should take a PRIORITY as well and override appointments with lower prio
        freeSlots = self.freeTimeSlots()
        return sum([timeSlot.timeInMinutes() for timeSlot in freeSlots])

    def timeInMinutes(self) -> int:
        return sum([timeSlot.timeInMinutes() for timeSlot in self.timeSlots])

    def addAppointment(self, appointment: Appointment):
        # Warn user if this overlaps another appointment, but accept it (overlapping appointments are valid)
        for existingAppointment in self.appointments:
            if existingAppointment.overlaps(appointment):
                print(f"WARNING: Added appointment overlaps with '{existingAppointment}'")

        self.appointments.append(appointment)

    def removeAppointment(self, name: str) -> bool:
        for app in self.appointments:
            if app.name == name:
                self.appointments.remove(app)
                return True
        return False

    def addTimeSlot(self, timeslot: TimeSlot):
        for existingTimeSlot in self.timeSlots:
            if existingTimeSlot.overlaps(timeslot):
                raise ValueError("TimeSlots may not overlap!")

        self.timeSlots.append(timeslot)

    def markSpecial(self):
        self.special = True
        # Remove all temporary timeslots
        self.timeSlots = [ts for ts in self.timeSlots if not ts.temporary]

    def unmarkSpecial(self):
        self.special = False
        # Re-add all temporary timeslots (This is done in the "ui.py" LUL)

    def export(self) -> dict:
        return {
            "dateString" : self.dateString,
            "timeSlots" : [ts.export() for ts in self.timeSlots if not ts.temporary],
            "appointments" : [app.export() for app in self.appointments],
            "special" : self.special
        }

    def __repr__(self) -> str:
        timeSlotString = "; ".join([repr(t) for t in self.timeSlots])
        appointmentString = "; ".join([repr(a) for a in self.appointments])

        # Mainly for debug
        if self.special:
            specialIdentifier = "S"
        else: # Default
            specialIdentifier = "D"

        return f"{self.dateString} {specialIdentifier} ({self.timeInMinutes()/60:.1f} h) Timeslots: [{timeSlotString}] Appointments: [{appointmentString}]"

    def __lt__(self, other) -> bool:
        return self.date < other.date

    def __gt__(self, other) -> bool:
        return self.date > other.date
