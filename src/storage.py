import json
import arrow
from task import Task
from day import Day
from timeslot import TimeSlot
from schedule import Schedule
from schedule_alg import calculateSchedule

# Save

def saveConfig(config: {}):
    save(config, "config")

def saveTasks(tasks: [Task]):
    parsedTasks = [task.export() for task in tasks]
    save(parsedTasks, "tasks")

def saveDays(days: [Day]):
    parsedDays = [day.export() for day in days]
    # print(parsedDays)
    save(parsedDays, "days")

def saveSchedule(schedule: Schedule):
    save(schedule.export(), "schedule")

def save(data, fileName: str):
    serialized = json.dumps(data)
    with open(f"./data/{fileName}.json", "w") as f:
        f.write(serialized)


# Load

def initDays(config: {}) -> [Day]:
    days = [Day.fromDict(d) for d in load("days")]

    # DO NOT Remove old days. They are necessary to properly recreate the schedule for past days

    # Create new days to remain at 1000 day threshold (20 for debug)

    # dayCount = 1000 # Real
    dayCount = 20 # Debug
    daysToCreate = dayCount - len(days)
    if days:
        startDate = days[-1].date
    else:
        startDate = arrow.now().date()

    currentDate = arrow.get(startDate)
    for _ in range(daysToCreate): # Fill up days to get up to dayCount
        currentDate = currentDate.shift(days=1)
        newDay = Day(currentDate, [], [])
        days.append(newDay)

    # Load config-TimeSlots onto days if they don't exist already
    for day in days:
        initDay(day, config) # Adds temporary timeslots based on config

    return days


def initDay(day: Day, config: {}):
    if day.special:  # No defaults are applied
        return
        
    if day.date.weekday() >= 5: # Weekend (Sat/Sun)
        lst = config["weekendTimeSlots"]
    else:
        lst = config["weekdayTimeSlots"]

    for timeSlotDict in lst:
        timeSlot = TimeSlot.fromDict(timeSlotDict, temporary=True) # These automatic TimeSlots are NOT persisted
        try:
            day.addTimeSlot(timeSlot)
        except ValueError:
            if timeSlot in day.timeSlots:
                pass # Already added
            else:
                print(f"WARNING: Default TimeSlot {timeSlot} could not be added to {day}")


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

def loadSchedule(tasks: [Task], days: [Day], debug=False) -> Schedule:
    scheduleMetaData = load("schedule")
    created = arrow.get(scheduleMetaData["created"], "DD.MM.YYYY HH:mm")
    lastWorkConfirmed = arrow.get(scheduleMetaData["lastWorkConfirmed"], "DD.MM.YYYY HH:mm")
    return calculateSchedule(tasks, days, created, lastWorkConfirmed=lastWorkConfirmed)
