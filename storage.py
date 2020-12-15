import json

def saveConfig(config):
    save(config, "config")

def saveTasks(tasks):
    save(tasks, "tasks")

def saveDays(days):
    save(days, "days")

def save(data, fileName: str):
    serialized = json.dumps(data)
    with open(f"./data/{fileName}.json","w") as f:
        f.write(serialized)