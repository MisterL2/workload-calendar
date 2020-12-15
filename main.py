from ui import mainMenu
import os

print("Welcome to the Workload Balancer v0.1")
if not os.path.isdir("./data"):
    print("No data storage found! Setting up...")
    os.mkdir("./data")

mainMenu()
