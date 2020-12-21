import json
import arrow
from task import Task
from day import Day

# Save

def saveConfig(config):
    save(config, "config")

def saveTasks(tasks):
    parsedTasks = [task.export() for task in tasks]
    save(parsedTasks, "tasks")

def saveDays(days):
    parsedDays = [day.export() for day in days]
    # print(parsedDays)
    save(parsedDays, "days")

def save(data, fileName: str):
    serialized = json.dumps(data)
    with open(f"./data/{fileName}.json", "w") as f:
        f.write(serialized)


# Load

def initDays() -> [Day]:
    days = [Day.fromDict(d) for d in load("days")]

    # Remove old days
    today = arrow.now().date() # Automatically considers timezone
    days = [day for day in days if day.date >= today]
    # Create new days to remain at 1000 day threshold (20 for debug)

    # dayCount = 1000 # Real
    dayCount = 20 # Debug
    daysToCreate = dayCount - len(days)
    if days:
        startDate = days[-1].date
    else:
        startDate = today

    currentDate = arrow.get(startDate)
    for _ in range(daysToCreate): # Fill up days to get up to dayCount
        currentDate = currentDate.shift(days=1)
        newDay = Day(currentDate, [], []) # TODO add actual timeslots for the day based on config default for that weekday
        days.append(newDay)

    return days

def initConfig() -> {}:
    config = load("config")

    defaults = {
        "weekdayTimeSlots" : [],
        "weekendTimeSlots" : []
    }

    # Fill missing keys with defaults
    for defaultKey in defaults.keys():
        if defaultKey not in config.keys():
            config[defaultKey] = defaults[defaultKey]
    return config

def loadTasks() -> [Task]:
    taskList = load("tasks")
    tasks = [Task.fromDict(d) for d in taskList]
    return tasks

def load(name: str):
    with open(f"./data/{name}.json") as f:
        out = f.read()
    return json.loads(out)