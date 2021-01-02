import arrow
from datetime import date
from timeslot import TimeSlot
from customtime import Time
from pyutil import intput
from task import Task
from day import Day
import util

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

def timeSlotInput(startTimeInfo: str, endTimeInfo: str) -> TimeSlot:
    while True:
        try:
            startTime = timeInput(startTimeInfo)
            endTime = timeInput(endTimeInfo)
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

def taskInput(hasDeadline=True) -> Task:
    name = input("Please enter the task name: ")
    minTime = floatInput("How much time does this task require AT LEAST (hours)? ") * 60
    maxTime = floatInput("How much time does this task require AT MOST (hours)? ") * 60

    priority = intput("Please enter a priority for this task (from 1 to 10): ", error="This is not a valid number! Please enter a valid whole number.")

    if hasDeadline:
        deadline = dayDateInput("Please enter the DAY ([DATEFORMAT]) of the deadline: ")
        time = timeInput("Please enter the TIME (HH:MM) of the deadline: ")
        deadline = arrow.get(deadline).shift(hours=time.hours, minutes=time.minutes)
    else:
        deadline = None

    minBlock = intput("What is the smallest block size that this task can be split up into (minutes)? ", "Invalid time! Please enter a valid whole number.")
    
    return Task(util.generateUUID(), name, minTime, maxTime, priority, deadline, minBlock)


def floatInput(info: str):
    while True:
        try:
            return float(input(info))
        except ValueError:
            print("Please return a valid number! Decimals are separated by '.', not ','!")

def validatedInput(info: str, error: str, validator):
    while True:
        userInput = input(info)
        if validator(userInput):
            return userInput
        print(error)

def taskSelection(tasks: [Task], info: str) -> Task:
    for i, task in enumerate(tasks):
        print(f"{i}: {showTaskSummary(task)}")

    while True:
        choice = intput(info, f"Error: Please select a number from 0 to {len(tasks) - 1}.")
        if choice >= 0 and choice < len(tasks):
            return tasks[choice]
        print(f"Error: Please select a number from 0 to {len(tasks) - 1}.")

def showTaskSummary(task: Task, recurring=False) -> str:
    # To do - show progress in ascii art, etc etc
    if recurring:
        return task.displayRecurringTask()
    else:
        return repr(task)

def dayInput(globalDays: [Day], info: str) -> Day:
    while True:
        try:
            dayDate = dayDateInput(info)
            return fetchDay(dayDate, globalDays)
        except IndexError as e:
            print(e)

def fetchDay(date: date, globalDays: [Day]) -> Day:
    for day in globalDays:
        if day.date == date:
            return day
    raise IndexError(f"Day '{date}' does not exist in the calendar. Is it in the past or very far in the future?")