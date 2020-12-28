from task import Task
from day import Day
import uuid

def getValueFromPriority(priority: float) -> float:
    return (0.0285 * priority**3) - (0.2668 * priority**2) + (1.4123 * priority) - 0.2978

def getTaskHappySignificance(task: Task, debug=False) -> float:
    if task.maxRemainingTime == 0:
        raise Exception("Error: Cannot calculate Significance for a task that is already completed!")

    totalValue = getValueFromPriority(task.priority)
    expectedDuration = task.avgTime
    valuePerMinute = totalValue / expectedDuration
    #taskProgress = task.progress

    # For ValueOnlyOnEnd Tasks
    remainingTime = task.maxRemainingTime
    remainingValuePerMinute = totalValue / remainingTime

    T = totalValue
    M = 0
    R = (totalValue / (1 - task.progress))**2
    if debug:
        print(f"T: {T}")
        print(f"R: {R}")

    # The significance values need to be unique for every task, so that the algorithm is deterministic (i.e. equal priority tasks are always sorted in the same order and not left to chance)
    uuidInt = task.uuidInt # Returns the 128-bit integer value. Max Value is 3.4 x 10**38
    unique = uuidInt / 10**40 # The unique value will be <= 0.034. This means it is larger than the rounding error of floats, but low enough not to interfere with priority.

    return 4.2 * T + R + unique
    #return (T * totalValue) + (M * valuePerMinute) + (R * remainingValuePerMinute)

def prioritiseTaskHappy(task1: Task, task2: Task, debug=False) -> Task: # "Happy" means that both tasks are possible before their deadline, regardless of order. The first task is returned
    t1 = getTaskHappySignificance(task1, debug=debug)
    t2 = getTaskHappySignificance(task2, debug=debug)

    if debug:
        print(f"Task #1 priority: {t1}")
        print(f"Task #2 priority: {t2}")

    if t1 > (t2 + 0.0001):
        return task1

    if t2 > (t1 + 0.0001):
        return task2

    # When equal, use name for priority
    if task1.name > task2.name:
        return task1
    if task2.name > task1.name:
        return task2
    
    raise Exception("Comparing two tasks with equal names! This is not possible (use unique identifiers)")