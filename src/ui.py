import arrow
from pyutil import intput
from task import *
from customtime import Time
from timeslot import TimeSlot
from appointment import Appointment
from day import Day
from datetime import date
import storage
import util

config = storage.initConfig() # Objects are stored in their exported form (dict) in the config
days = storage.initDays(config)
tasks = storage.loadTasks()

def autosave():
    # Autosaving
    storage.saveConfig(config)
    storage.saveDays(days)
    storage.saveTasks(tasks)

def mainMenu():
    while True:
        autosave()
        try:
            print("1) Show Active Tasks")
            print("2) Show All Days (debug)")
            print("3) Add Task")
            print("4) Add TimeSlots")
            print("5) Add Appointment")
            print("9) Exit")
            choice = intput("", "Not a valid number!")
            
            if choice == 1:
                showActiveTasks()
            elif choice == 2:
                showDays() # Debug
            elif choice == 3:
                addTask() 
            elif choice == 4:
                addTimeSlotsMenu()
            elif choice == 5:
                addAppointment()
            elif choice == 9:
                return
            else:
                print("Invalid number!")
        except KeyboardInterrupt:
            print("Aborted by user.")
            


def addTask():
    try:
        name = input("Please enter the task name: ")
        valid = False
        while not valid:
            try:
                timeRequirement = float(input("How much time does this task require (hours)? ")) * 60
                valid = True
            except ValueError:
                print("Please return a valid number! Decimals are separated by '.', not ','!")

        priority = intput("Please enter a priority for this task (from 1 to 10): ", error="This is not a valid number! Please enter a valid whole number.")



        deadline = dayDateInput("Please enter the DAY ([DATEFORMAT]) of the deadline: ")
        time = timeInput("Please enter the TIME (HH:MM) of the deadline: ")
        deadline = deadline.shift(hours=time.hours, minutes=time.minutes)

        minBlock = intput("What is the smallest block size that this task can be split up into (minutes)? ","Invalid time! Please enter a valid whole number.")
        deadline = util.dateString(deadline, time=True)
        task = Task(name, timeRequirement, priority, deadline, minBlock)
        tasks.append(task)
        
        print("Task added successfully!")

    except KeyboardInterrupt:
        print("Aborted by user. Returning to main menu")

def showActiveTasks(): 
    print("=================================")
    if tasks:
        for task in tasks:
            showTaskSummary(task)
    else:
        print("You have no active tasks!")
    print("=================================")

def showTaskSummary(task: Task):
    # To do - show progress in ascii art, etc etc
    print(task)

def showDays(): # Debug
    for day in days:
        print(day)

def timeSlotInput(info1: str, info2: str) -> TimeSlot:
    while True:
        try:
            startTime = timeInput(info1)
            endTime = timeInput(info2)
            return TimeSlot(startTime, endTime)
        except ValueError as e:
            print(e)

def timeInput(info: str) -> Time:
    while True:
        try:
            timeString = input(info)
            time = Time.fromString(timeString)
            return time
        except (IndexError, ValueError):
            print("Invalid Time!")

# If the String contains the placeholder `[DATEFORMAT]`, it will be replaced by the actual date format.
def dayDateInput(info: str) -> date:
    while True:
        try:
            dateformat = "DD.MM.YYYY"
            dateString = input(info.replace("[DATEFORMAT]", dateformat))
            return arrow.get(dateString, dateformat).date()
        except Exception as e:
            print(e)
            print("Invalid Date!")

def dayInput(info: str) -> Day:
    while True:
        try:
            dayDate = dayDateInput(info)
            return fetchDay(dayDate)
        except IndexError as e:
            print(e)

def fetchDay(date: date) -> Day:
    for day in days:
        if day.date == date:
            return day
    raise IndexError(f"Day '{date}' does not exist in the calendar. Is it in the past or very far in the future?")

def addAppointment():
    name = input("Please enter a name for the Appointment: ")
    day = dayInput("Please enter the DAY ([DATEFORMAT]) of the Appointment: ")
    timeSlot = timeSlotInput("Please enter the start time of the Appointment (HH:MM): ", "Please enter the end time of the Appointment (HH:MM): ")
    appointment = Appointment(name, timeSlot)

    day.addAppointment(appointment)

def addTimeSlot(weekday: bool):
    while True:
        try:
            timeSlot = timeSlotInput("Please enter the start time of the TimeSlot (HH:MM): ", "Please enter the end time of the TimeSlot (HH:MM): ")
            if weekday:
                lst = config["weekdayTimeSlots"]
            else:
                lst = config["weekendTimeSlots"]

            for timeSlotDict in lst:
                ts = TimeSlot.fromDict(timeSlotDict)
                if ts.overlaps(timeSlot):
                    raise ValueError(f"Overlapping TimeSlot in Config: {ts}. Cannot add new time slot!")
            lst.append(timeSlot.export())
            return
        except ValueError as e:
            print(e)

def addTimeSlotsMenu():
    while True:
        autosave()
        print("1) Add Weekday TimeSlot")
        print("2) Add Weekend TimeSlot")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            addTimeSlot(weekday=True)
        elif choice == 2:
            addTimeSlot(weekday=False)
        elif choice == 9:
            return
        else:
            print("Invalid number!")

print("Thanks for using the workload balancer!")
