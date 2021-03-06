from datetime import date
import util
from timeslot import TimeSlot
from comparable import Comparable
from appointment import Appointment
from customtime import Time
from task import Task

class Day(Comparable):
    @staticmethod
    def fromDict(valueDict: dict, globalTasks=None):
        parsedDate = util.dateStringToArrow(valueDict["dateString"]).date()
        timeSlots = [TimeSlot.fromDict(t, globalTasks=globalTasks) for t in valueDict["timeSlots"]]
        appointments = [Appointment.fromDict(appDict) for appDict in valueDict["appointments"]]
        isSpecial = valueDict["special"]
        return Day(parsedDate, timeSlots, appointments, special=isSpecial)

    def __init__(self, date: date, timeSlots: [TimeSlot], appointments: [Appointment], special=False): # Remember: don't use mutables as default params
        self.special = special
        self.date = date
        self.timeSlots = [] # Always
        self.appointments = appointments
        
        for timeSlot in timeSlots:
            self.addTimeSlot(timeSlot) # This validates that there are no overlapping timeslots
    
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

    # Returns the day's schedule. This means:
    # 1. Non-Empty TimeSlots (i.e. with a TaskOrAppointment assigned to it)
    # 2. Appointment-TimeSlots
    @property
    def daySchedule(self) -> [TimeSlot]:
        schedule = [ts.fullCopy() for ts in self.timeSlots if ts.taskOrAppointment is not None]
        for app in self.appointments:
            appts = app.timeSlot.copy() # Does not include TaskOrAppointment reference
            appts.taskOrAppointment = app 
            schedule.append(appts)
        return sorted(schedule, key=lambda ts: ts.startTime)

    @property
    def dayScheduleWorkTime(self) -> int:
        return int(sum([ts.durationInMinutes for ts in self.daySchedule]))

    def freeTimeSlots(self, before=None, after=None) -> [TimeSlot]: # Returns a NEW DEEPCOPIED LIST containing new objects / copies
        # At this point, priority could be used to determine if appointments should get thrown out
        blocking_appointments = self.appointments.copy()
        virtualAppointments = [] # Blocking appointments to simulate some constraint, i.e. after/before
        if before is not None and before != Time(23, 59):
            before = Appointment("VIRTUAL_APP_BEFORE", TimeSlot(before, Time(23, 59)))
            virtualAppointments.append(before)
        if after is not None and after != Time(0, 0):
            after = Appointment("VIRTUAL_APP_AFTER", TimeSlot(Time(0, 0), after))
            virtualAppointments.append(after)

        blocking_appointments += virtualAppointments

        freeSlots = []
        for timeSlot in self.timeSlots:
            # TimeSlots with a TaskOrAppointment assigned to it are not free
            if timeSlot.taskOrAppointment is not None:
                continue

            # Calculate overlap with appointments and perhaps split up TimeSlots as necessary
            currentTimeSlots = [timeSlot.copy()]
            for appointment in blocking_appointments:
                newTimeSlots = []
                for currentTimeSlot in currentTimeSlots:
                    newTimeSlots += currentTimeSlot.nonOverlap(appointment.timeSlot)
                currentTimeSlots = newTimeSlots.copy() # .copy() is very important; mutation danger
            freeSlots += currentTimeSlots.copy()
        return freeSlots

    def freeTimeInMinutes(self, before=None, after=None) -> int: # Later on this should take a PRIORITY as well and override appointments with lower prio
        freeSlots = self.freeTimeSlots(before=before, after=after)
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

    def addTimeSlot(self, timeSlot: TimeSlot):
        for existingTimeSlot in self.timeSlots:
            if existingTimeSlot.overlaps(timeSlot):
                raise ValueError("TimeSlots may not overlap!")

        if self.special and timeSlot.temporary:
            print("WARNING: Trying to add temporary timeSlot to special day")
        else:
            self.timeSlots.append(timeSlot)

        self.timeSlots = sorted(self.timeSlots, key=lambda ts: ts.startTime)

    def removeTimeSlot(self, timeSlot: TimeSlot):
        self.timeSlots.remove(timeSlot)

    # This should only ever be performed on a copy of the days by the schedule / schedule_alg and NEVER the persisted version
    def scheduleTask(self, newTimeSlot: TimeSlot, task: Task, debug=False):
        if debug:
            print(f"Trying to schedule {newTimeSlot}!")
            print(f"Available TimeSlots: {self.timeSlots}")

        startTime = newTimeSlot.startTime
        endTime = newTimeSlot.endTime
        # Find matching TimeSlot
        for ts in self.timeSlots:
            # If already scheduled
            if ts.taskOrAppointment is not None:
                continue

            # If the TimeSlot includes the startTime/endTime (i.e. Scenario [{}])
            if ts.startTime <= startTime and endTime <= ts.endTime:
                # Remove the old TimeSlot
                self.timeSlots.remove(ts)

                # Add the task to it
                timeSlotToBeScheduled = newTimeSlot.copy()
                timeSlotToBeScheduled.taskOrAppointment = task

                # Calculate the nonOverlap of the existing TimeSlot with the new one. For example:
                # If they are identical, newTimeSlots = []
                # If the old ts was 15:00 - 18:00 and the new one 16:00 - 17:00, then this contains 15:00 - 16:00 and 17:00 - 18:00
                newTimeSlots = ts.nonOverlap(timeSlotToBeScheduled)

                # Add the TimeSlot to be scheduled to the list. The list now contains TimeSlots covering the full area of the original TimeSlot
                newTimeSlots.append(timeSlotToBeScheduled)

                # Re-add the TimeSlots to the day
                for new in newTimeSlots:
                    self.addTimeSlot(new) # Re-use the addTimeSlot logic. It also auto-sorts
                return # This is called separately for each (partial) TimeSlot that is supposed to be filled, so all work is done here
        raise Exception(f"Could not find a matching TimeSlot for {startTime} - {endTime}!")


    def markSpecial(self):
        self.special = True
        # Remove all temporary timeslots
        self.timeSlots = [ts for ts in self.timeSlots if not ts.temporary]

    def unmarkSpecial(self):
        self.special = False
        self.timeSlots = []
        # Re-add all temporary timeslots (This is done in the "ui.py" LUL)

    def export(self, forSchedule=False) -> dict:
        return {
            "dateString" : self.dateString,
            "timeSlots" : [ts.export(forSchedule=forSchedule) for ts in self.timeSlots if (not ts.temporary) or forSchedule], # If forSchedule, export all. Otherwise export only non-temporary
            "appointments" : [app.export() for app in self.appointments],
            "special" : self.special
        }

    def copy(self): # Is a Deepcopy
        newDay = Day.fromDict(self.export())
        newDay.timeSlots = [ts.fullCopy() for ts in self.timeSlots] # To avoid temporary tasks from being forgotten during the export
        return newDay

    @property
    def headline(self) -> str:
        weekday = self.date.strftime("%A").capitalize()
        return f"*{weekday} {self.dateString} ({self.dayScheduleWorkTime/60:.1f} h)*"

    def detailedView(self) -> str:
        dayScheduleString = "\n\t".join([repr(t) for t in self.daySchedule])
        if dayScheduleString == "": 
            dayScheduleString = "<<< Nothing scheduled on this day! Enjoy your freedom ;) >>>"
        
        return f"{self.headline}\n\t{dayScheduleString}"

    def __repr__(self) -> str:
        timeSlotString = "; ".join([repr(t) for t in self.timeSlots])
        appointmentString = "; ".join([repr(a) for a in self.appointments])
        weekdayIdentifier = self.date.strftime("%A").upper()[:2]

        # Mainly for debug
        if self.special:
            specialIdentifier = "S"
        else: # Default
            specialIdentifier = "D"

        return f"{self.dateString} ({weekdayIdentifier}) {specialIdentifier} ({self.timeInMinutes()/60:.1f} h) Timeslots: [{timeSlotString}] Appointments: [{appointmentString}]"

    def __lt__(self, other) -> bool:
        return self.date < other.date

    def __gt__(self, other) -> bool:
        return self.date > other.date
