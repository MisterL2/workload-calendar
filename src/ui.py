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
from scheduleexceptions import DateNotFoundException
import ui_util

config = storage.initConfig() # Objects are stored in their exported form (dict) in the config
days = storage.initDays(config)
tasks = storage.loadTasks(config, days)
schedule = storage.loadSchedule(tasks, days)

def autosave():
    # Autosaving
    print("Autosaving...")
    storage.saveConfig(config)
    storage.saveDays(days)
    storage.saveTasks(tasks)
    storage.saveSchedule(schedule)

def autoupdate():
    global config, days, tasks, schedule
    print("Autoupdating...")
    #print("Loading config...")
    config = storage.initConfig() # Objects are stored in their exported form (dict) in the config
    #print("Loading days...")
    days = storage.initDays(config)
    #print("Loading tasks...")
    tasks = storage.loadTasks(config, days)
    #print("Loading schedule...")
    schedule = storage.loadSchedule(tasks, days)
    confirmRecentWork()
    #print("Calculating new schedule...")
    schedule = calculateSchedule(days, tasks, schedule, util.smoothCurrentArrow()) # This IS a PERFORMANCE KILLER

def onInit():
    print("Initialising...")
    # Initialisation hooks
    confirmRecentWork()

def isTaskFinished(task: Task, status: int):
    print(f"TODO: The user would be ask to confirm if this task is finished; it has status {status}")


def confirmRecentWork():
    # Check if any planned tasks/timeslots of the schedule have occurred between the last time work was confirmed
    recentlyCompleted = schedule.recentlyCompleted()
    #print(f"Recently completed: {recentlyCompleted}")
    if recentlyCompleted:
        print("Please confirm the following schedule events that should have occurred since your last visit (y/n):")

    # TODO IMPORTANT TODO Consider the potential timeslot that we are currently in, which is not finished yet but rather WIP, particularly for new schedule creation.
    # TODO ^^^ Need to consider the amount of hours currently scheduled for the task when building a new schedule.
    # i.e. if we are in the middle of a 4h-block of some Task A, we need consider that these 4h are already scheduled for that task (but not counted towards task progress yet)
    # This needs to be considered, otherwise Task A is overscheduled, as the 4h block is scheduled again

    taskStates = {}

    # Algorithm:

    # Confirm?
    # If yes, continue
    #   If no -> Completely missing or Different TimeSlot?
    #   If completely missing, continue
    #   If different TimeSlot, allow user to enter a timeslot and add that amount of completionTime to the task. TimeSlot must be within the original timeslot

    for recentCompletion in recentlyCompleted:
        dateString, timeSlot, task = recentCompletion["dateString"], recentCompletion["timeSlot"], recentCompletion["task"]
        answer = ui_util.validatedInput(f"[{dateString} {timeSlot.timeString}] - {task.name}\n", "Please answer with Y or N", lambda inp: inp.lower() in {'y', 'n'})
        if answer.lower() == 'y': # Add completion time
            status = task.addCompletionTime(timeSlot.durationInMinutes)
            taskStates[task] = status
        else:
            answer = int(ui_util.validatedInput("Was this timeslot missed out completely (1) or only partially (2)", "Error: Please answer with 1 or 2", lambda inp: inp in {'1', '2'}))
            if answer == 1:
                print("Thanks! Skipping...")
                continue
            elif answer == 2:
                while True:
                    ts = ui_util.timeSlotInput("Please enter the start time of the correct time slot (HH:MM): ", "Please enter the end time of the correct time slot (HH:MM): ")
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
            answer = ui_util.validatedInput("Is the task already completed (y/n)? ", "Error: Please answer with Y or N", lambda inp: inp.lower() in {'y','n'})
            # TODO Refactor to isTaskFinished
            if answer.lower() == 'y':
                pass # TODO Mark task as completed
            elif answer.lower() == 'n':
                continue
            else:
                print("Impossible error A77FD223GS in UI")
        elif taskStatus == 2:
            print(f"The following task has exceeded its MAXIMUM time requirement: {task.name}")
            # TODO Refactor to isTaskFinished
            answer = ui_util.validatedInput("Is the task completed (y/n)? ", "Error: Please answer with Y or N", lambda inp: inp.lower() in {'y', 'n'})
            if answer.lower() == 'y':
                pass # TODO Mark task as completed
            elif answer.lower() == 'n':
                while True:
                    additionalHours = ui_util.floatInput("How much longer do you think the task will take (hours)? ")
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
            print("1) Calendar")
            print("2) Tasks")
            print("3) Daily TimeSlots")
            print("4) Edit a specific Day")
            print("7) Show entire Schedule (debug)")
            print("8) Show All Days (debug)")
            print("9) Exit")
            choice = intput("", "Not a valid number!")
            
            if choice == 1:
                viewCalendarMenu()
            elif choice == 2:
                viewTaskMenu()
            elif choice == 3:
                changeTimeSlotsMenu()
            elif choice == 4:
                daySelectionMenu()
            elif choice == 7:
                showSchedule() # Debug
            elif choice == 8:
                showDays() # Debug
            elif choice == 9:
                return
            else:
                print("Invalid number!")
        except KeyboardInterrupt:
            print("Aborted by user.")

def showDays(): # Debug
    for day in days:
        print(day)

def showSchedule():
    print(schedule)

def viewTaskMenu():
    
    while True:
        autosave()
        print("1) View Tasks")
        print("2) Add Task")
        print("3) Add time to task")
        print("4) Wipe Task (Remove completely & retroactively)")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            showActiveTasks()
        elif choice == 2:
            addTaskMenu()
        elif choice == 3:
            addTaskCompletionTime()
        elif choice == 4:
            wipeTask()
        elif choice == 9:
            return
        else:
            print("Invalid number!")

def addTaskMenu():
    while True:
        autosave()
        print("1) Task WITH deadline")
        print("2) Task WITHOUT deadline")
        print("3) Recurring (i.e. weekly) Task")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            addTask(hasDeadline=True)
        elif choice == 2:
            addTask(hasDeadline=False)
        elif choice == 3:
            addRecurringTaskToConfig()
        elif choice == 9:
            return
        else:
            print("Invalid number!")

def addTaskCompletionTime():
    selectedTask = ui_util.taskSelection(tasks, "Please select the task you wish to add time to: ")
    while True:
        minutesToAdd = intput("How much time do you wish to add to this task (MINUTES)? ", "Error: Please enter a positive number.")
        if minutesToAdd > 0:
            status = selectedTask.addCompletionTime(minutesToAdd)
            if status > 0:
                isTaskFinished(selectedTask, status)
            return
        print("Error: Please enter a positive number.")


def wipeTask():
    regularTasks = getActiveRegularTasks()
    taskToWipe = ui_util.taskSelection(regularTasks, "Please select the task you wish to remove: ")
    tasks.remove(taskToWipe)
    schedule.wipeTask(taskToWipe)
    print(f"Task `{taskToWipe}` was removed!")

def getActiveRegularTasks():
    return [task for task in tasks if task.recurringTaskUUID is None] # Filter out generated (recurring) tasks

def addRecurringTaskToConfig():
    try:
        task = ui_util.taskInput(hasDeadline=False)
        task.updateValue("recurringTaskUUID", task.uuid)
        startDay = ui_util.dayDateInput("What is the START date of this repeating task? ")
        start = arrow.Arrow(startDay.year, startDay.month, startDay.day, hour=0, minute=0, microsecond=0)
        task.updateValue("start", start)
        while True:
            intervalDays = intput("What is the interval (days) that this task repeats in (weekly=7)? ", error="Please enter a valid number")
            if intervalDays < 1:
                print("The interval must be at least 1 day")
            else:
                break
        
        config["recurringTasks"].append({"task" : task, "interval" : intervalDays})
        print("Repeating Task added successfully!")
    except KeyboardInterrupt:
        print("Aborted by user. Returning to main menu")

def addTask(hasDeadline=True):
    try:
        task = ui_util.taskInput(hasDeadline=hasDeadline)
        tasks.append(task)
        print("Task added successfully!")
    except KeyboardInterrupt:
        print("Aborted by user. Returning to main menu")


def showActiveTasks(): 
    print("=================================")
    regularTasks = [task for task in tasks if task.recurringTaskUUID is None] # Filter out generated (recurring) tasks
    if regularTasks or config["recurringTasks"]:
        if regularTasks:
            print("Regular Tasks:")
            for task in regularTasks:
                print(ui_util.showTaskSummary(task))
        else:
            print("~~~No regular Tasks~~~")
        
        if config["recurringTasks"]:
            currentArrow = util.smoothCurrentArrow()
            futureGeneratedTasks = [task for task in tasks if task.recurringTaskUUID is not None and task.start < currentArrow]
            if futureGeneratedTasks:
                print("Recurring Tasks:")
                for recurringTaskDict in config["recurringTasks"]:
                    #print(f"{ui_util.showTaskSummary(recurringTaskDict['task'],recurring=True)} (Interval: {recurringTaskDict['interval']} days) from {util.dateString(recurringTaskDict['startDate'])}")
                    recurringTaskUUID = recurringTaskDict["task"].recurringTaskUUID
                    # Find the generated task relating to the current week
                    generatedTasks = sorted([task for task in futureGeneratedTasks if task.recurringTaskUUID == recurringTaskUUID], key=lambda task: task.deadline)

                    for gtask in generatedTasks:
                        if gtask.start <= currentArrow and gtask.deadline >= currentArrow:
                            print(f"{ui_util.showTaskSummary(gtask)} (Interval: {recurringTaskDict['interval']} days)")
                            break
            else:
                print("~~~No recurring Tasks in current week~~~")
        else:
            print("~~~No recurring Tasks~~~")
    else:
        print("You have no active tasks!")
    print("=================================")


def addAppointment(day: Day):
    name = input("Please enter a name for the Appointment: ")
    timeSlot = ui_util.timeSlotInput("Please enter the start time of the Appointment (HH:MM): ", "Please enter the end time of the Appointment (HH:MM): ")
    appointment = Appointment(name, timeSlot)

    day.addAppointment(appointment)

def removeAppointment(day: Day):
    name = input("Please enter the name of the Appointment: ")
    appointmentExisted = day.removeAppointment(name)
    if appointmentExisted:
        print(f"Appointment '{name}' removed.")
    else:
        print(f"Error: No Appointment with name '{name}' on this day!")

def addRegularTimeSlot(weekday: bool):
    while True:
        try:
            timeSlot = ui_util.timeSlotInput("Please enter the start time of the TimeSlot (HH:MM): ", "Please enter the end time of the TimeSlot (HH:MM): ")
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

def removeRegularTimeSlot(weekday: bool):
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
        if len(config["weekdayTimeSlots"]) > 0:
            print("3) Remove Weekday TimeSlot")
        else:
            print("3) Remove Weekday TimeSlot *not available/no weekday timeslots*")
        if len(config["weekendTimeSlots"]) > 0:
            print("4) Remove Weekend TimeSlot")
        else:
            print("4) Remove Weekend TimeSlot *not available/no weekend timeslots*")
        print("9) Back to Main Menu")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            addRegularTimeSlot(weekday=True)
        elif choice == 2:
            addRegularTimeSlot(weekday=False)
        elif choice == 3 and len(config["weekdayTimeSlots"]) > 0:
            removeRegularTimeSlot(weekday=True)
        elif choice == 4 and len(config["weekendTimeSlots"]) > 0:
            removeRegularTimeSlot(weekday=False)
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
    day = ui_util.dayInput(days, "Please enter the DAY ([DATEFORMAT]) you want to select: ")
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
        print("5) Add Custom TimeSlot")
        print("6) Remove Custom TimeSlot")
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
        elif choice == 5:
            addTimeSlot(day)
        elif choice == 6:
            removeCustomTimeSlot(day)
        elif choice == 9:
            return
        else:
            print("Invalid number!")

def addTimeSlot(day: Day):
    while True:
        ts = ui_util.timeSlotInput("Please enter the START time (HH:MM) of the TimeSlot: ", "Please enter the END time (HH:MM) of the TimeSlot: ")
        try:
            return day.addTimeSlot(ts)
        except ValueError as e:
            print(e)


def removeCustomTimeSlot(day: Day):
    print(day.headline)
    customTimeSlots = [ts for ts in day.timeSlots if not ts.temporary] # Filters out any default TimeSlots, which cannot be removed here (but instead in `Daily TimeSlots`)
    if customTimeSlots:
        for i, ts in enumerate(customTimeSlots):
            print(f"{i}: {ts}")
        while True:
            choice = intput("Please select the TimeSlot that you wish to remove: ", f"Please select a number between 0 and {len(customTimeSlots)-1}")
            if choice >= 0 and choice < len(customTimeSlots):
                selected = customTimeSlots[choice]
                day.removeTimeSlot(selected)
                print(f"TimeSlot `{selected}` removed!")
                return
            print(f"Please select a number between 0 and {len(customTimeSlots)-1}")
    else:
        print("There are no custom TimeSlots for this day!")


def displayToday():
    displayScheduleDay(arrow.now().date())

def displayScheduleDay(date: date):
    try:
        day = schedule.getDay(date)
        print(day.detailedView())
    except DateNotFoundException as e:
        print(e)

def showCurrentWeek():
    showWeek(arrow.now().date())

def showWeek(anyDateOfThatWeek: date):
    try:
        week = schedule.getWeek(anyDateOfThatWeek)
        print(week)
    except DateNotFoundException as e:
        print(e)

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
            displayScheduleDay(ui_util.dayDateInput("Please enter the DAY ([DATEFORMAT]) that you wish to look at: "))
        elif choice == 4:
            showWeek(ui_util.dayDateInput("Please enter any DAY ([DATEFORMAT]) from the week that you wish to look at: "))
        elif choice == 9:
            return
        else:
            print("Invalid number!")

print("Thanks for using the workload balancer!")
