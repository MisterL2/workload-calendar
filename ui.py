import arrow
from pyutil import intput
from task import *
from storage import *
import util

config = {}
futureDays = []
tasks = []

def mainMenu():
    # Autosaving
    saveConfig(config)
    saveDays(futureDays)
    saveTasks(tasks)
    try:
        print("1) Add Task")
        print("2) Show Active Tasks")
        choice = intput("", "Not a valid number!")
        
        if choice == 1:
            createTask()
        elif choice == 2:
            showActiveTasks()
        else:
            print("Invalid number!")
            mainMenu()
    except KeyboardInterrupt:
        print("Program stopped by user.")


def createTask():
    try:
        name = input("Please enter the task name: ")

        valid = False
        while not valid:
            try:
                timeRequirement = float(input("How much time does this task require (hours)? ")) * 60
                valid = True
            except ValueError:
                print("Please return a valid number! Decimals are separated by '.', not ','!")

        priority = intput("Please enter a priority for this task (from 1 to 10): ", error="This is not a valid number! Please enter a valid whole number.")

        validDay = False
        while not validDay:
            try:
                dateformat = "DD.MM.YYYY"
                dateString = input(f"Please enter the DAY ({dateformat}) of the deadline: ")
                deadline = arrow.get(dateString, dateformat)
                validDay = True
            except (IndexError, ValueError) as e:
                print(e)
                print("Invalid Date!")

        validTime = False
        while not validTime:
            try:
                timeString = input("Please enter the TIME (HH:MM) of the deadline: ")
                hours = int(timeString.split(":")[0])
                minutes = int(timeString.split(":")[1])

                deadline = deadline.shift(hours=hours, minutes=minutes)

                validTime = True
            except (IndexError, ValueError):
                print("Invalid Date!")

        minBlock = intput("What is the smallest block size that this task can be split up into (minutes)? ","Invalid time! Please enter a valid whole number.")
        deadline = util.dateString(deadline, time=True)
        task = Task(name, timeRequirement, priority, deadline, minBlock)
        tasks.append(task)
        
        print("Task added successfully!")

    except KeyboardInterrupt:
        print("Aborted by user. Returning to main menu")
    mainMenu()

def showActiveTasks(): 
    print("=================================")
    if tasks:
        for task in tasks:
            showTaskSummary(task)
    else:
        print("You have no active tasks!")
    print("=================================")
    mainMenu()

def showTaskSummary(task: Task):
    # To do - show progress in ascii art, etc etc
    print(task)

print("Thanks for using the workload balancer!")
