from ui import mainMenu
import os

print("Welcome to the Workload Balancer v0.2-Alpha")
if not os.path.isdir("./data"):
    print("No data storage found! Setting up...")
    os.mkdir("./data")

mainMenu()
