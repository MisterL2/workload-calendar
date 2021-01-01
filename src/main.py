import os

print("Welcome to the Workload Balancer v0.3-Alpha")
if not os.path.isdir("./data"):
    print("No data storage found! Setting up...")
    os.mkdir("./data")
    with open("./data/schedule.json", "w") as f:
        f.write("{}")
    with open("./data/tasks.json", "w") as f:
        f.write("[]")
    with open("./data/days.json", "w") as f:
        f.write("[]")
    with open("./data/config.json", "w") as f:
        f.write("{}")

from ui import mainMenu # The import also runs all the global-scoped commands in UI, aka all the loading procedures.
mainMenu()
