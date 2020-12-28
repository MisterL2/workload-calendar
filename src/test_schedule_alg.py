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

    def test_isSolvable_Standard_DifferentDeadline(self): # iSSDD
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]

        paramDictLst = [
            {"name": "iSSDD-0.1T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("02.01.2099 10:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.2F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 09:00", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.3T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("05.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("07.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.4T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 04:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("09.01.2099 00:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 12:45", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.5F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 04:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("09.01.2099 00:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 07:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.6T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.5, "deadline": arrow.get("02.01.2099 16:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("08.01.2099 23:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.7F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:45", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0.2, "deadline": arrow.get("04.01.2099 23:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.8T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("03.01.2099 16:00", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.9F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("03.01.2099 14:30", "DD.MM.YYYY HH:mm")},
                ]
            },
        ]


        for paramDict in paramDictLst:
            with self.subTest(name=paramDict["name"]):
                tasks = []
                for taskDict in paramDict["tasks"]:
                    task = Task(util.generateUUID(), "Task #1", taskDict["time"], taskDict["time"], taskDict["priority"], taskDict["deadline"], 0)
                    task.addCompletionTime(taskDict["progress"] * taskDict["time"])
                    tasks.append(task)
                
                days = paramDict["days"]

                debug = False
                result = schedule_alg.isSolvable(tasks, days, arrow.Arrow.fromdate(days[0].date), debug=debug)
                self.assertEqual(result, paramDict["solution"])