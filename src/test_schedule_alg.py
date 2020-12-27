from unittest import TestCase
from task import Task
from day import Day
from timeslot import TimeSlot
import arrow
import util
import schedule_alg

class ScheduleTest(TestCase):
    def test_isSolvable_Standard_AllSameDeadline(self): # iSSASD
        deadline = arrow.get("31.01.2099", "DD.MM.YYYY")
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]
        paramDictLst = [
            {"name": "iSSASD-0.1T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.8},
                {"time": 1200, "priority": 8, "progress": 0},
                {"time": 900, "priority": 6, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.2T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0},
                {"time": 600, "priority": 5, "progress": 0.4},
                {"time": 600, "priority": 7, "progress": 0.1},
                ]
            },
            {"name": "iSSASD-0.3T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0},
                {"time": 2400, "priority": 7, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.4F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0},
                {"time": 2401, "priority": 7, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.5F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 12000, "priority": 5, "progress": 0}
                ]
            },
            {"name": "iSSASD-0.6T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0.5}, # So 3000 remaining
                {"time": 6000, "priority": 7, "progress": 0.8}, # So 1200 remaining
                ]
            },
            {"name": "iSSASD-0.7F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0.5},
                {"time": 6000, "priority": 7, "progress": 0},
                ]
            }
        ]
        for paramDict in paramDictLst:
            with self.subTest(name=paramDict["name"]):
                tasks = []
                for taskDict in paramDict["tasks"]:
                    task = Task(util.generateUUID(), "Task #1", taskDict["time"], taskDict["time"], taskDict["priority"], deadline, 0)
                    task.addCompletionTime(taskDict["progress"] * taskDict["time"])
                    tasks.append(task)
                
                days = paramDict["days"]

                debug = False
                result = schedule_alg.isSolvable(tasks, days, arrow.Arrow.fromdate(days[0].date), debug=debug)
                self.assertEqual(result, paramDict["solution"])

