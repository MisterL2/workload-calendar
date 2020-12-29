from task import Task
from day import Day
import arrow
from typing import Union
from customtime import Time
from schedule import Schedule
from timegraph import TimeGraph
from priority_alg import getTaskHappySignificance
import util

# DEFINITIONS
# "Happy" -> Every Task can be done, no sacrifices must be made, even if they all take their MaxTime
# "Risky" -> Every Task could be done, but only if their MinTime is used (NOTE: Low priority feature; Needs to decide which tasks to drop to provide more safety to the more valuable/high priority tasks (or if none should be dropped and #yolo))
# "Sad" -> Not every Task can be completed, so some tasks must be sacrificed

# This is the MAIN function that is called, which delegates to all the other functions
def calculateSchedule(tasks: [Task], days: [Day], start: arrow.Arrow, debug=False) -> Schedule:
    # Creates a clean copy of the tasks and days, so that no evil mutation occurs
    tmpDays = sorted([day.copy() for day in days], key=lambda d: d.date)
    tmpTasks = sorted([task.copy() for task in tasks], key=lambda t: t.deadline)

    if isSolvable(tasks, days, start, useMinimum=False):
        return calculateHappySchedule(tmpTasks, tmpDays, start, debug=debug)
    elif isSolvable(tasks, days, start, useMinimum=True):
        return calculateSadSchedule(tmpTasks, tmpDays, start, debug=debug)
        #return calculateRiskySchedule(tmpTasks, tmpDays, start)
    else:
        return calculateSadSchedule(tmpTasks, tmpDays, start, debug=debug)

def calculateHappySchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow, debug=False) -> Schedule:
    for tmpTask in tmpTasks:
        if tmpTask.maxRemainingTime <= 0:
            raise Exception(f"Already completed tmpTask! MaxRemainingTime: {tmpTask.maxRemainingTime}")

    if debug:
        print("TmpTasks (at start of calculateHappySchedule):")
        print(tmpTasks)

    # It is possible for all tasks to fit (Happy Schedule)
    happySchedule = Schedule(tmpDays)

    # Find date of last day
    endDate = arrow.get(tmpDays[-1].date)
    endDate.hour = 23
    endDate.minute = 59

    # totalAvailableTimeInMinutes = getFreeTimeBetweenPoints(tmpDays, start, endDate)

    # TODO: Consider minBlock for all of these calculations! The "area" is just a collection of minutes, we need to consider the individual timeslot blocks
    # For this, the getFreeSpaceBetween and its related day-class-methods need to be adjusted & tested too

    amountOfTimeScheduled = 0

    while True:
        # When all tasks are scheduled (they are removed from tmpTasks when fully scheduled)
        if len(tmpTasks) == 0:
            return happySchedule

        # Build timegraph based on deadlines
        tg = buildHappyTimeGraph(tmpTasks, tmpDays, start)

        if debug:
            print(tg)
        # Get highest priority Task
        highestPriorityTask = findHighestPriorityTask(tmpTasks)

        # Check if there are any TimeIntervals at all (i.e. tasks with deadlines).
        # If only tasks without deadlines remain, then fullyFree is True
        if len(tg.timeIntervals) == 0:
            fullyFree = True
        else: # If there are deadlines remaining, check if the highestProrityTask fits inside of it completely (`fullyFree`)
            # Look at the area before the first TimeInterval of the TimeGraph
            ti = tg.timeIntervals[0]

            # Calculate available space
            spaceBeforeFirst = tg.freeSpaceBetween(amountOfTimeScheduled, ti.startTimeInMinutes)

            fullyFree = spaceBeforeFirst > highestPriorityTask.maxRemainingTime

        if fullyFree:
            # If area is FREE -> Schedule something into that area (TODO: consider minBlock)
            amountOfTimeScheduled += highestPriorityTask.maxRemainingTime
            happySchedule.scheduleTask(highestPriorityTask, debug=debug)
            tmpTasks.remove(highestPriorityTask)
            continue
        else:
            # Find the task with the closest deadline. If there are several with the same deadline, the one with highest significance is picked
            closest = findClosestUnfinishedDeadline(tmpTasks)

            # If free time is > 0 and <= 3h
            # 1. If there is a task with higher significance than 'closest' that fits into these 3h, schedule it and end iteration (`continue`)
            # 2. If 1. is not possible, schedule 'closest'
            if spaceBeforeFirst > 0 and spaceBeforeFirst <= 180:
                betterOptions = list(filter(lambda t: t.maxRemainingTime < spaceBeforeFirst and (getTaskHappySignificance(t) > getTaskHappySignificance(closest)), tmpTasks))
                if len(betterOptions) > 0:
                    bestOption = sorted(betterOptions, key=getTaskHappySignificance, reverse=True)[0]

                    amountOfTimeScheduled += bestOption.maxRemainingTime
                    happySchedule.scheduleTask(bestOption, debug=debug)
                    tmpTasks.remove(bestOption)
                    continue # End this iteration of the while loop here, as a task was already scheduled.
                

            # If free time is == 0 -> Schedule 'closest' (only option)
            # If free time is > 3h -> Schedule 'closest' (make room for higher priority task later on)
            # If area is NOT FREE -> out of the unfinished deadline tasks, schedule the task with the CLOSEST deadline (if there are several, the highest priority one is picked)
            amountOfTimeScheduled += closest.maxRemainingTime
            happySchedule.scheduleTask(closest) # This mutates the task "closest" by adding completionTime to it
            tmpTasks.remove(closest)


def findHighestPriorityTask(tasks: [Task]) -> Task:
    unfinished = list(filter(lambda t: t.maxRemainingTime > 0, tasks))
    return max(unfinished, key=getTaskHappySignificance)

def findClosestUnfinishedDeadline(tasks: [Task]) -> Task:
    unfinishedWithDeadline = list(filter(lambda t: t.hasDeadline() and t.maxRemainingTime > 0, tasks))
    closestDeadline = min(unfinishedWithDeadline, key=lambda task: task.deadline).deadline

    # There might be several tasks with the closest deadline. Return the one with highest priority
    tasksWithClosestDeadline = list(filter(lambda t: t.deadline == closestDeadline, unfinishedWithDeadline))
    return max(tasksWithClosestDeadline, key=getTaskHappySignificance)

def buildHappyTimeGraph(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow) -> TimeGraph:
    # Build a timegraph for the tasks that have a deadline and aren't finished yet
    deadlineTasks = unfinishedDeadlineTasks(tmpTasks)
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

def calculateRiskySchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow, debug=False) -> Schedule:
    raise Exception("Risky schedule is not implemented and a low priority feature")

def calculateSadSchedule(tmpTasks: [Task], tmpDays: [Day], start: arrow.Arrow, debug=False) -> Schedule:
    raise Exception("Sad schedule is not implemented yet")

def unfinishedDeadlineTasks(tasks: [Task]) -> [Task]:
    return list(filter(lambda task: task.hasDeadline() and task.maxRemainingTime > 0, tasks))

def isSolvable(tasks: [Task], days: [Day], start: arrow.Arrow, useMinimum=False, debug=False) -> bool:
    if (util.smoothCurrentArrow() > start):
        raise Exception("Cannot solve an algorithm for the past")
    # TO DO - Incorporate current day / time as lower minimum!
    sortedTasks = sorted(unfinishedDeadlineTasks(tasks), key=lambda task: task.deadline)
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

def getFreeTimeBetweenPoints(days: [Day], start: arrow.Arrow, end: arrow.Arrow) -> int: # In Minutes
    if start == end:
        return 0
    
    sortedDays = sorted(days, key=lambda d: d.date)

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
            if day.date == endDate: # If it is ALSO equal to the endDate (i.e. startDate and endDate are the same day)
                return day.freeTimeInMinutes(after=startTime, before=endTime) # Return immediately, as this is the only day (since startDate==endDate)
            else:
                freeMinutes += day.freeTimeInMinutes(after=startTime)
                continue

        # Days after or equal to the end date
        if day.date > endDate:
            print(f"WARNING: This scenario [debug-id: schedule_alg:AAA123] should not occur! Last day of time windows was likely not calculated correctly. DayDate: {day.date} | EndDate: {endDate}")
            print(f"Start: {start} | End: {end}")
            return freeMinutes
        elif day.date == endDate:
            freeMinutes += day.freeTimeInMinutes(before=endTime)
            return freeMinutes # This is the last valid day, return immediately

        # Normal day
        freeMinutes += day.freeTimeInMinutes()

    return freeMinutes
