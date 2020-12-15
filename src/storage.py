import json

def saveConfig(config):
    save(config, "config")

def saveTasks(tasks):
    parsedTasks = [task.export() for task in tasks]
    save(parsedTasks, "tasks")

def saveDays(days):
    parsedDays = [day.export() for day in days]
    save(days, "days")

def save(data, fileName: str):
    serialized = json.dumps(data)
    with open(f"./data/{fileName}.json","w") as f:
        f.write(serialized)