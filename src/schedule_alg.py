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
def calculateSchedule(globalDays: [Day], tasks: [Task], currentSchedule: Schedule, start: arrow.Arrow, debug=False) -> Schedule:
    currentTime = util.smoothCurrentArrow()
    if start < currentTime:
        raise Exception("Cannot calculate a schedule for the past")

    days = currentSchedule.days()
    oldDays = [day.copy() for day in days if day.date <= start.date()] # Contains all days PRIOR to start date (last is popped off)
    
    oldTimeSlots = []
    if oldDays: # On initial creation, there are no old days
        lastDay = oldDays.pop() # This day is changed after the current timeslot and kept the same before.
        splitTime = Time(start.hour, start.minute)
        
        for ts in lastDay.timeSlots:
            if ts.endTime > splitTime and ts.startTime < splitTime:
                # Update start time to be the end of the current timeslot

                # Update Arrow object only if it isn't before the smoothCurrentArrow()
                splitArrow = arrow.Arrow(start.year, start.month, start.day, hour=ts.endTime.hours, minute=ts.endTime.minutes)
                if splitArrow >= currentTime:
                    start = splitArrow
                    splitTime = Time(start.hour, start.minute)
            
            if ts.startTime < splitTime and ts.taskOrAppointment is not None:
                oldTimeSlots.append(ts)


    startIndex = None
    for i, day in enumerate(globalDays):
        if day.date == start.date():
            startIndex = i
            break
    else:
        raise Exception("Error in schedule_alg 555255GGG")
    
    
    newDays = [day.copy() for day in globalDays[startIndex:]]

    # Remove TimeSlots prior to start
    firstNewDay = newDays[0]

    oldTimeSlotsToRemove = []
    for ts in firstNewDay.timeSlots:
        if ts.startTime < splitTime:
            oldTimeSlotsToRemove.append(ts)
    for otstr in oldTimeSlotsToRemove:
        firstNewDay.timeSlots.remove(otstr)

    for oldTimeSlot in oldTimeSlots:
        firstNewDay.addTimeSlot(oldTimeSlot)
    

    lastWorkConfirmed = currentSchedule.lastWorkConfirmed

    if lastWorkConfirmed is None:
        lastWorkConfirmed = start.clone()
    
    # Creates a clean copy of the tasks and days, so that no evil mutation occurs
    newDays = sorted(newDays, key=lambda d: d.date)
    tmpTasks = sorted([task.copy() for task in tasks], key=lambda t: t.deadline)
    
    if isSolvable(tasks, newDays, start, useMinimum=False):
        happySchedule = calculateHappySchedule(tmpTasks, newDays, lastWorkConfirmed, start, debug=debug) # Adds the history (previous schedule) to the newly calculated schedule
        happySchedule.addHistory(oldDays)
        return happySchedule
    elif isSolvable(tasks, newDays, start, useMinimum=True):
        riskySchedule = calculateSadSchedule(tmpTasks, newDays, lastWorkConfirmed, start, debug=debug)
        riskySchedule.addHistory(oldDays)
        return riskySchedule
        #return calculateRiskySchedule(tmpTasks, newDays, created=start)
    else:
        sadSchedule = calculateSadSchedule(tmpTasks, newDays, lastWorkConfirmed, start, debug=debug)
        sadSchedule.addHistory(oldDays)
        return sadSchedule

def calculateHappySchedule(tmpTasks: [Task], tmpDays: [Day], lastWorkConfirmed: arrow.Arrow, start: arrow.Arrow, debug=False) -> Schedule:
    # Only calculates the new schedule with NO REGARD TO THE PAST SCHEDULE
    
    for tmpTask in tmpTasks:
        if tmpTask.maxRemainingTime <= 0:
            print(f"WARNING: Already completed tmpTask! MaxRemainingTime: {tmpTask.maxRemainingTime}")

    if debug:
        print("TmpTasks (at start of calculateHappySchedule):")
        print(tmpTasks)

    # It is possible for all tasks to fit (Happy Schedule)
    happySchedule = Schedule(tmpDays, lastWorkConfirmed, created=start)

    # Find date of last day
    endDate = arrow.get(tmpDays[-1].date)
    endDate.hour = 23
    endDate.minute = 59

    # totalAvailableTimeInMinutes = getFreeTimeBetweenPoints(tmpDays, start, endDate)

    # TODO: Consider minBlock for all of these calculations! The "area" is just a collection of minutes, we need to consider the individual timeslot blocks
    # For this, the getFreeSpaceBetween and its related day-class-methods need to be adjusted & tested too
    # Keep in mind that minBlocks may change, i.e. there might be 300 free minutes with minBlock 30-compatible times, but after scheduling i.e. a 25min task into a 50-minute slot, the remaining 25min are also lost to minBlock and could cause a deadline clash.

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
        if debug: print(f"Highest priority task: {highestPriorityTask}")

        # Check if there are any TimeIntervals at all (i.e. tasks with deadlines).
        # If only tasks without deadlines remain, then fullyFree is True
        if len(tg.timeIntervals) == 0:
            fullyFree = True
        else: # If there are deadlines remaining, check if the highestPriorityTask fits inside of it completely (`fullyFree`)
            # Look at the area before the first TimeInterval of the TimeGraph
            ti = tg.timeIntervals[0]

            # Calculate available space
            spaceBeforeFirst = tg.freeSpaceBetween(amountOfTimeScheduled, ti.startTimeInMinutes)

            fullyFree = spaceBeforeFirst >= highestPriorityTask.maxRemainingTime

        if fullyFree:
            # If area is FREE -> Schedule the highest priority task into that area
            amountOfTimeScheduled += highestPriorityTask.maxRemainingTime
            happySchedule.scheduleTask(highestPriorityTask, start, debug=debug) # This mutates the tmpTask by adding completionTime to it
            tmpTasks.remove(highestPriorityTask)
            continue
        else:
            # Find the task with the closest deadline. If there are several with the same deadline, the one with highest significance is picked
            closest = findClosestUnfinishedDeadline(tmpTasks)

            # TODO: For the cases below, weigh off the delay on the highest priority task vs the priority-difference between the highest priority task that fits and closest

            # If free time is > 0 and <= 8h
            # 1. If there is a task with higher significance than 'closest' that fits into the first 3h, schedule it and end iteration (`continue`)
            # 2. If there is a task with higher significance than 'closest' that fits into the first 8h AND has at least 0.8x the significance of the highestPriorityTask, schedule it and end iteration (`continue`)
            # 3. If 1. and 2. are not possible, schedule 'closest'
            if spaceBeforeFirst > 0 and spaceBeforeFirst <= 640:
                betterOptions = list(filter(
                            lambda t:
                                t.maxRemainingTime < spaceBeforeFirst
                                and getTaskHappySignificance(t) > getTaskHappySignificance(closest)
                                and (
                                    t.maxRemainingTime <= 180 # Scenario 1.
                                    or
                                    getTaskHappySignificance(highestPriorityTask)*0.8 < getTaskHappySignificance(t) # Scenario 2.
                                    )
                            , tmpTasks))
                if len(betterOptions) > 0:
                    bestOption = sorted(betterOptions, key=getTaskHappySignificance, reverse=True)[0]

                    amountOfTimeScheduled += bestOption.maxRemainingTime
                    happySchedule.scheduleTask(bestOption, start, debug=debug) # This mutates the task by adding completionTime to it
                    tmpTasks.remove(bestOption)
                    continue # End this iteration of the while loop here, as a task was already scheduled.
                

            # If free time is == 0 -> Schedule 'closest' (only option)
            # If free time is > 8h -> Schedule 'closest' (make room for higher priority task later on)
            # If area is NOT FREE -> out of the unfinished deadline tasks, schedule the task with the CLOSEST deadline (if there are several, the highest priority one is picked)
            amountOfTimeScheduled += closest.maxRemainingTime
            happySchedule.scheduleTask(closest, start, debug=debug) # This mutates the task "closest" by adding completionTime to it
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

def calculateRiskySchedule(tmpTasks: [Task], tmpDays: [Day], lastWorkConfirmed: arrow.Arrow, start: arrow.Arrow, debug=False) -> Schedule:
    raise Exception("Risky schedule is not implemented and a low priority feature")

def calculateSadSchedule(tmpTasks: [Task], tmpDays: [Day], lastWorkConfirmed: arrow.Arrow, start: arrow.Arrow, debug=False) -> Schedule:
    print(tmpTasks)
    print("WARNING: Happy schedule is not possible; Using sad schedule algorithm. This algorithm is HIGHLY EXPERIMENTAL and may drop tasks arbitrarily.")
    # Temporary solution: Just delete low priority tasks till it fits
    prioritisedTasks = sorted(tmpTasks, key=getTaskHappySignificance, reverse=True)
    while not isSolvable(prioritisedTasks, tmpDays, start, debug=debug):
        removedTask = prioritisedTasks.pop()
        print(f"WARNING: Removing Task {removedTask.name} to convert to happy schedule.")
    return calculateHappySchedule(prioritisedTasks, tmpDays, lastWorkConfirmed, start)
    


def unfinishedDeadlineTasks(tasks: [Task]) -> [Task]:
    return list(filter(lambda task: task.hasDeadline() and task.maxRemainingTime > 0, tasks))

def isSolvable(tasks: [Task], days: [Day], start: arrow.Arrow, useMinimum=False, debug=False) -> bool:
    if start < util.smoothCurrentArrow():
        raise Exception("Cannot calculate a schedule for the past")

    # Is used to solve a schedule from a past standpoint, i.e. where start < current. This is used for recreating a past schedule for example.
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
