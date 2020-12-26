from task import Task
from day import Day

def getValueFromPriority(priority: float) -> float:
    return (0.0285 * priority**3) - (0.2668 * priority**2) + (1.4123 * priority) - 0.2978

def getTaskHappySignificance(task: Task) -> float:
    totalValue = getValueFromPriority(task.priority)
    expectedDuration = task.avgTime
    valuePerMinute = totalValue / expectedDuration
    #taskProgress = task.progress

    # For ValueOnlyOnEnd Tasks
    remainingTime = task.maxRemainingTime
    remainingValuePerMinute = totalValue / remainingTime

    T = 1
    M = 1
    R = 1

    return (T * totalValue) + (M * valuePerMinute) + (R * remainingValuePerMinute)

def prioritiseTaskHappy(task1: Task, task2: Task) -> Task: # "Happy" means that both tasks are possible before their deadline, regardless of order. The first task is returned
    t1 = getTaskHappySignificance(task1)
    t2 = getTaskHappySignificance(task2)
    if t1 > (t2 + 0.0001):
        return task1
    elif t2 > (t1 + 0.0001):
        return task2
    else: # Equal
        if task1.name > task2.name:
            return task1
        elif task2.name > task1.name:
            return task2
        else:
            raise Exception("Comparing two tasks with equal names! This is not possible (use unique identifiers)")