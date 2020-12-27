from task import Task
from day import Day
import arrow
from typing import Union
from customtime import Time
from schedule import Schedule
from virtualday import VirtualDay
from virtualtimeslot import VirtualTimeSlot
from timegraph import TimeGraph
import util

# DEFINITIONS
# "Happy" -> Every Task can be done, no sacrifices must be made, even if they all take their MaxTime
# "Risky" -> Every Task could be done, but only if their MinTime is used (NOTE: Low priority feature; Needs to decide which tasks to drop to provide more safety to the more valuable/high priority tasks (or if none should be dropped and #yolo))
# "Sad" -> Not every Task can be completed, so some tasks must be sacrificed

# This is the MAIN function that is called, which delegates to all the other functions
def calculateSchedule(tasks: [Task], days: [Day], start: arrow.Arrow) -> Schedule:
    # Creates a clean copy of the tasks and days, so that no evil mutation occurs
    tmpDays = sorted([day.copy() for day in days], key=lambda d: d.date)
    tmpTasks = sorted([task.copy() for task in tasks], key=lambda t: t.deadline)

    if isSolvable(tasks, days, start, useMinimum=False):
        return calculateHappySchedule(tmpTasks, tmpDays, start)
    elif isSolvable(tasks, days, start, useMinimum=True):
        return calculateSadSchedule(tmpTasks, tmpDays, start)
        #return calculateRiskySchedule(tmpTasks, tmpDays, start)
    else:
        return calculateSadSchedule(tmpTasks, tmpDays, start)

def calculateHappySchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow) -> Schedule:
    # It is possible for all tasks to fit (Happy Schedule)

    # Find date of last day
    endDate = arrow.get(tmpDays[-1].date)
    endDate.hour = 23
    endDate.minute = 59

    totalAvailableTimeInMinutes = getFreeTimeBetweenPoints(tmpDays, start, endDate)

    while True:
        # Build timegraph based on deadlines
        timegraph = buildHappyTimeGraph(tmpTasks, tmpDays, start)

        # Look at the area before the first TimeInterval of the TimeGraph

        # If area is FREE -> Schedule something into that area (consider minBlock)

        # If area is NOT FREE -> out of the unfinished deadline tasks, schedule the task with the CLOSEST deadline


    

def buildHappyTimeGraph(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow) -> TimeGraph:
    # Build a timegraph for the tasks that have a deadline and aren't finished yet
    deadlineTasks = filter(lambda dt: dt.hasDeadline() and dt.maxRemainingTime > 0, tmpTasks)
    deadlineTimeStampsInMinutes = {deadlineTask: getFreeTimeBetweenPoints(tmpDays, start, deadlineTask.deadline) for deadlineTask in deadlineTasks}
    
    timegraph = TimeGraph() # The TimeGraph calculates which times need to be reserved to ensure that no deadlines are missed, even with overlapping deadlines/TimeIntervals

    for deadlineTask in deadlineTasks:
        endTimeInMinutes = deadlineTimeStampsInMinutes[deadlineTask]
        durationInMinutes = deadlineTask.maxRemainingTime # Takes into consideration already performed progress towards it
        if durationInMinutes == 0: # Task is already completed
            continue
        name = deadlineTask.name
        # addTimeInterval will automatically make room for it in the TimeGraph by shifting itself or conflicting TimeIntervals to earlier points
        timegraph.addTimeInterval(name, endTimeInMinutes, durationInMinutes)

    return timegraph

def calculateRiskySchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow) -> Schedule:
    raise Exception("Risky schedule is not implemented and a low priority feature")

def calculateSadSchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow) -> Schedule:
    raise Exception("Sad schedule is not implemented yet")

def isSolvable(tasks: [Task], days: [Day], start: arrow.Arrow, useMinimum=False, debug=False) -> bool:
    if (util.smoothCurrentArrow() > start):
        raise Exception("Cannot solve an algorithm for the past")
    # TO DO - Incorporate current day / time as lower minimum!
    sortedTasks = sorted(tasks, key=lambda task: task.deadline)
    sortedDays = sorted(days, key=lambda day: day.date)

    currentCumulativeWorkload = 0
    currentCumulativeFreeTime = 0
    currentTaskDeadline = start
    for task in sortedTasks:
        nextDeadline = task.deadline

        # On the first iteration (Note: This considers appointments to have absolute priority currently)
        currentFreeTime = getFreeTimeBetweenPoints(sortedDays, currentTaskDeadline, nextDeadline)
        
        if useMinimum:
            currentCumulativeWorkload += task.minRemainingTime
        else:
            currentCumulativeWorkload += task.maxRemainingTime
        currentCumulativeFreeTime += currentFreeTime

        if debug:
            print(f"cCWorkload: {currentCumulativeWorkload}")
            print(f"cCFreeTime: {currentCumulativeFreeTime}")

        if currentCumulativeWorkload > currentCumulativeFreeTime:
            return False # In these cases, it is not possible to meet all deadlines

        currentTaskDeadline = nextDeadline
    
    return True

def getFreeTimeBetweenPoints(sortedDays: [Day], start: arrow.Arrow, end: arrow.Arrow) -> int: # In Minutes
    if start == end:
        return 0
    
    startDate = start.date()
    endDate = end.date()
    startTime = Time(start.hour, start.minute)
    endTime = Time(end.hour, end.minute)

    # Collect time inbetween
    freeMinutes = 0
    for day in sortedDays:

        # Days before or equal to the start date
        if day.date < startDate:
            continue
        elif day.date == startDate:
            freeMinutes += day.freeTimeInMinutes(after=startTime)
            continue

        # Days after or equal to the end date
        if day.date > endDate:
            print("WARNING: This scenario [debug-id: AAA123] should not occur! Last day of time windows was likely not calculated correctly")
            break
        elif day.date == endDate:
            freeMinutes += day.freeTimeInMinutes(before=endTime)
            break

        # Normal day
        freeMinutes += day.freeTimeInMinutes()

    return freeMinutes
