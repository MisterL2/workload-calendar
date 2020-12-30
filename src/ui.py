import arrow
from pyutil import intput
from task import Task
from customtime import Time
from timeslot import TimeSlot
from appointment import Appointment
from day import Day
from datetime import date
import storage
import util
from schedule_alg import calculateSchedule

config = storage.initConfig() # Objects are stored in their exported form (dict) in the config
days = storage.initDays(config)
tasks = storage.loadTasks()
schedule = storage.loadSchedule(tasks, days)

def autosave():
    # Autosaving
    storage.saveConfig(config)
    storage.saveDays(days)
    storage.saveTasks(tasks)
    storage.saveSchedule(schedule)

def autoupdate():
    global config, days, tasks, schedule
    config = storage.initConfig() # Objects are stored in their exported form (dict) in the config
    days = storage.initDays(config) # This might be a PERFORMANCE KILLER
    tasks = storage.loadTasks()
    schedule = storage.loadSchedule(tasks, days) # This might be a PERFORMANCE KILLER

def onInit():
    print("Initialising...")
    # Initialisation hooks

    # Check if any planned tasks/timeslots of the schedule have occurred between the last time work was confirmed
    print("Loading schedule...")
    recentlyCompleted = schedule.recentlyCompleted()
    if recentlyCompleted:
        print("Please confirm the following schedule events that should have occurred since your last visit (y/n):")

    # TODO IMPORTANT TODO Consider the potential timeslot that we are currently in, which is not finished yet but rather WIP, particularly for new schedule creation.
    # It would be bad to remove the current timeslot in the creation of a new schedule... imagine the user is 3h into a 4h timeslot and then another task is scheduled there semi-retroactively
    
    taskStates = {}

    # Algorithm:

    # Confirm?
    # If yes, continue
    #   If no -> Completely missing or Different TimeSlot?
    #   If completely missing, continue
    #   If different TimeSlot, allow user to enter a timeslot and add that amount of completionTime to the task. TimeSlot must be within the original timeslot

    for recentCompletion in recentlyCompleted:
        dateString, timeSlot, task = recentCompletion["dateString"], recentCompletion["timeSlot"], recentCompletion["task"]
        answer = validatedInput(f"[{dateString} {timeSlot.timeString}] - {task.name}\n", "Please answer with Y or N", lambda inp: inp.lower() in {'y', 'n'})
        if answer.lower() == 'y': # Add completion time
            status = task.addCompletionTime(timeSlot.durationInMinutes)
            taskStates[task] = status
        else:
            answer = validatedInput("Was this timeslot missed out completely (1) or only partially (2)", "Error: Please answer with 1 or 2", lambda inp: inp in {'1', '2'})
            if answer == 1:
                print("Thanks! Skipping...")
                continue
            elif answer == 2:
                while True:
                    ts = timeSlotInput("Please enter the start time of the correct time slot (HH:MM): ", "Please enter the end time of the correct time slot (HH:MM): ")
                    if timeSlot.containsOrEquals(ts):
                        status = task.addCompletionTime(ts.durationInMinutes)
                        taskStates[task] = 0
                        print(f"Thanks! Added with new time slot: {ts.timeString}")
                        break
                    else:
                        print(f"Error! The time slot needs to be a portion of the original timeslot ({timeSlot.timeString})!")
            else:
                print("Impossible error FF33fSSF1 in UI")

    schedule.lastWorkConfirmed = arrow.now() # Update this so it doesn't get triggered again for the same events

    # Algorithm
    # Confirm?
    # If yes, continue (task completed, deal with that)
    # If no, show current progress and ask for how many hours to add. Validate that the amount of hours to add causes maxRemainingTime to be > 0

    for task in taskStates.keys():
        taskStatus = taskStates[task]
        if taskStatus == 1:
            print(f"The following task has exceeded its MINIMUM time requirement: {task.name}")
            answer = validatedInput("Is the task already completed (y/n)? ", "Error: Please answer with Y or N", lambda inp: inp.lower() in {'y','n'})
            if answer.lower() == 'y':
                pass # TODO Mark task as completed
            elif answer.lower() == 'n':
                continue
            else:
                print("Impossible error A77FD223GS in UI")
        elif taskStatus == 2:
            print(f"The following task has exceeded its MAXIMUM time requirement: {task.name}")
            answer = validatedInput("Is the task completed (y/n)? ", "Error: Please answer with Y or N", lambda inp: inp.lower() in {'y', 'n'})
            if answer.lower() == 'y':
                pass # TODO Mark task as completed
            elif answer.lower() == 'n':
                while True:
                    additionalHours = floatInput("How much longer do you think the task will take (hours)? ")
                    if additionalHours > 0:
                        task.addTimeRequirement(round(additionalHours * 60))
                        if task.maxRemainingTime <= 0:
                            raise Exception("Task still has a maxRemainingTime <= 0 after an additional TimeRequirement was added to it")
                        break
                    else:
                        print("Error: The amount of hours to be added must be > 0")

            else:
                print("Impossible error A77FD223GS in UI")
            

def mainMenu():
    onInit()
    while True:
        autosave()
        autoupdate() # Reloads EVERYTHING. This is good as it auto-applies config updates, but also might be a PERFORMANCE KILLER
        try:
            print("1) Show Active Tasks")
            print("2) Open Calendar")
            print("3) Add Task")
            print("4) Change daily TimeSlots")
            print("5) Edit a specific Day")
            print("8) Show All Days (debug)")
            print("9) Exit")
            choice = intput("", "Not a valid number!")
            
            if choice == 1:
                showActiveTasks()
            elif choice == 2:
                viewCalendarMenu() 
            elif choice == 3:
                addTask() 
            elif choice == 4:
                changeTimeSlotsMenu()
            elif choice == 5:
                daySelectionMenu()
            elif choice == 8:
                showDays() # Debug
            elif choice == 9:
                return
            else:
                print("Invalid number!")
        except KeyboardInterrupt:
            print("Aborted by user.")
            


def addTask():
    try:
        name = input("Please enter the task name: ")
        minTime = floatInput("How much time does this task require AT LEAST (hours)? ") * 60
        maxTime = floatInput("How much time does this task require AT MOST (hours)? ") * 60

        priority = intput("Please enter a priority for this task (from 1 to 10): ", error="This is not a valid number! Please enter a valid whole number.")

        deadline = dayDateInput("Please enter the DAY ([DATEFORMAT]) of the deadline: ")
        time = timeInput("Please enter the TIME (HH:MM) of the deadline: ")
        deadline = deadline.shift(hours=time.hours, minutes=time.minutes)

        minBlock = intput("What is the smallest block size that this task can be split up into (minutes)? ", "Invalid time! Please enter a valid whole number.")
        deadline = util.dateString(deadline, time=True)
        task = Task(util.generateUUID(), name, minTime, maxTime, priority, deadline, minBlock)
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

def addAppointment(day: Day):
    name = input("Please enter a name for the Appointment: ")
    timeSlot = timeSlotInput("Please enter the start time of the Appointment (HH:MM): ", "Please enter the end time of the Appointment (HH:MM): ")
    appointment = Appointment(name, timeSlot)

    day.addAppointment(appointment)

def removeAppointment(day: Day):
    name = input("Please enter the name of the Appointment: ")
    appointmentExisted = day.removeAppointment(name)
    if appointmentExisted:
        print(f"Appointment '{name}' removed.")
    else:
        print(f"Error: No Appointment with name '{name}' on this day!")

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
            lst.append(timeSlot.export()) # Modifies the config
            return
        except ValueError as e:
            print(e)

def removeTimeSlot(weekday: bool):
    if weekday:
        timeSlots = config["weekdayTimeSlots"]
        print("The following TimeSlots are scheduled for weekdays: ")
    else:
        timeSlots = config["weekendTimeSlots"]
        print("The following TimeSlots are scheduled for weekends: ")
    
    for i, timeSlotDict in enumerate(timeSlots):
        ts = TimeSlot.fromDict(timeSlotDict)
        print(f"{i}: {ts.timeString}")
    
    while True:
        choice = intput("Please select the ID of the TimeSlot you would like to remove: ", "That is not a valid ID (should be a simple number)!")
        if choice >= 0 and choice < len(timeSlots):
            del timeSlots[choice] # Modifies the config
            print("TimeSlot was removed!")
            return
        else:
            print(f"Invalid choice! Needs to be between 0 and {len(timeSlots)}")

def changeTimeSlotsMenu():
    while True:
        autosave()
        print("1) Add Weekday TimeSlot")
        print("2) Add Weekend TimeSlot")
        print("3) Remove Weekday TimeSlot")
        print("4) Remove Weekend TimeSlot")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            addTimeSlot(weekday=True)
        elif choice == 2:
            addTimeSlot(weekday=False)
        elif choice == 3:
            removeTimeSlot(weekday=True)
        elif choice == 4:
            removeTimeSlot(weekday=False)
        elif choice == 9:
            return
        else:
            print("Invalid number!")


def markDaySpecial(day):
    day.markSpecial() # Fully handled by day

def unmarkDaySpecial(day):
    day.unmarkSpecial()
    storage.initDay(day, config) # Re-adding temporary/default TimeSlots

def daySelectionMenu():
    day = dayInput("Please enter the DAY ([DATEFORMAT]) you want to select: ")
    return editDayMenu(day)

def editDayMenu(day: Day):
    while True:
        autosave()
        print("=====================")
        print(day)
        print("1) Mark as special (No Default Timestamps)")
        print("2) Mark as normal (Default Timestamps apply)")
        print("3) Add Appointment")
        print("4) Remove Appointment")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            markDaySpecial(day)
        elif choice == 2:
            unmarkDaySpecial(day)
        elif choice == 3:
            addAppointment(day)
        elif choice == 4:
            removeAppointment(day)
        elif choice == 9:
            return
        else:
            print("Invalid number!")

def validatedInput(info: str, error: str, validator):
    while True:
        userInput = input(info)
        if validator(userInput):
            return userInput
        print(error)

def floatInput(info: str):
    while True:
        try:
            return float(input(info))
        except ValueError:
            print("Please return a valid number! Decimals are separated by '.', not ','!")

def displayToday():
    displayScheduleDay(arrow.now().date())

def displayScheduleDay(date: date):
    day = schedule.getDay(date)
    print(day.detailedView())

def showCurrentWeek():
    showWeek(arrow.now().date())

def showWeek(anyDateOfThatWeek: date):
    week = schedule.getWeek(anyDateOfThatWeek)
    # TODO: Print week nicely

def viewCalendarMenu():
    while True:
        print("1) View current week")
        print("2) View current day")
        print("3) View a specific day")
        print("4) View a specific week")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            showCurrentWeek()
        elif choice == 2:
            displayToday()
        elif choice == 3:
            displayScheduleDay(dayDateInput("Please enter the DAY ([DATEFORMAT]) that you wish to look at: "))
        elif choice == 4:
            showWeek(dayDateInput("Please enter any DAY ([DATEFORMAT]) from the week that you wish to look at: "))
        elif choice == 9:
            return
        else:
            print("Invalid number!")

print("Thanks for using the workload balancer!")
