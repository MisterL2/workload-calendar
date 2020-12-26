from task import Task
from day import Day
from arrow import Arrow
from typing import Union
from customtime import Time
import util

def isSolvable(tasks: [Task], days: [Day], start: Arrow, useMinimum=False) -> bool:
    # TO DO - Incorporate current day / time as lower minimum!
    sortedTasks = sorted(tasks, key=lambda task: task.deadline)
    sortedDays = sorted(days, key=lambda day: day.date)

    currentCumulativeWorkload = 0
    currentCumulativeFreeTime = 0
    currentTaskDeadline = start
    for task in sortedTasks:
        nextDeadline = task.deadline

        # On the first iteration (Note: This considers appointments to have absolute priority currently)
        currentFreeTime = getFreeTimeBetweenPoints(days, currentTaskDeadline, nextDeadline)
        
        currentCumulativeWorkload += task.maxTime()
        currentCumulativeFreeTime += currentFreeTime

        if currentCumulativeWorkload > currentCumulativeFreeTime:
            return False # In these cases, it is not possible to meet all deadlines

        currentTaskDeadline = nextDeadline
    
    return True

def getFreeTimeBetweenPoints(sortedDays: [Day], start: Arrow, end: Arrow) -> int: # In Minutes
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
            print("WARNING: This scenario AAA123 should not occur! Last day of time windows was likely not calculated correctly")
            break
        elif day.date == endDate:
            freeMinutes += day.freeTimeInMinutes(before=endTime)
            break

        # Normal day
        freeMinutes += day.freeTimeInMinutes()

    return freeMinutes



