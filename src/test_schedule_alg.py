from unittest import TestCase
from task import Task
from day import Day
from timeslot import TimeSlot
import arrow
import util
import schedule_alg

class ScheduleTest(TestCase):
    def test_calculate_Easy_HappySchedule(self): # cEHS
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]
        paramDictLst = [
            {"name": "cEHS-0.1", "days": defaultDays.copy(),
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                    {"taskName": "Task #2", "time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                    {"taskName": "Task #3", "time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #3"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("05.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 11:30", "taskName": "Task #3"},
                            {"timeslotString": "11:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("06.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 14:00", "taskName": "Task #1"},
                            {"timeslotString": "14:00 - 17:00", "taskName": None},
                        ]
                    },
                    {"date": arrow.get("07.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": None},
                            {"timeslotString": "13:00 - 17:00", "taskName": None},
                        ]
                    }
                ]
            }
        ]

        for paramDict in paramDictLst:
            with self.subTest(name=paramDict["name"]):
                tasks = []
                for taskDict in paramDict["tasks"]:
                    task = Task(util.generateUUID(), taskDict["taskName"], taskDict["time"], taskDict["time"], taskDict["priority"], taskDict["deadline"], 0)
                    task.addCompletionTime(taskDict["progress"] * taskDict["time"])
                    tasks.append(task)
                
                days = paramDict["days"]

                debug = False

                schedule = schedule_alg.calculateSchedule(tasks, days, arrow.Arrow.fromdate(days[0].date), debug=debug)

                print(schedule)

                for solutionDict in paramDict["expected"]: # Go through each expected day and see if the timeslots are assigned correctly
                    actualDay = schedule.getDay(solutionDict["date"])
                    expectedTimeSlots = []
                    for expectedTimeSlotDict in solutionDict["timeslots"]:
                        ts = TimeSlot.fromString(expectedTimeSlotDict["timeslotString"])

                        # If there is a task name specified, attach the task to the expectedTimeSlot
                        if expectedTimeSlotDict["taskName"] is not None:
                            # Find the task with the correct taskName
                            for task in tasks:
                                if task.name == expectedTimeSlotDict["taskName"]:
                                    ts.task = task
                                    break # Inner for loop
                        expectedTimeSlots.append(ts)

                    self.assertEqual(len(expectedTimeSlots), len(actualDay.timeSlots), f"Incorrect length of TimeSlots: Expected {len(expectedTimeSlots)} but got {len(actualDay.timeSlots)}!")
                    for i in range(len(expectedTimeSlots)):
                        expectedTimeSlot = expectedTimeSlots[i]
                        actualTimeSlot = actualDay.timeSlots[i]
                        # Check if the TimeSlots are equal (This only checks if their times are equal. It does not consider the associated task)
                        self.assertEqual(expectedTimeSlot, actualTimeSlot, f"TimeSlot with index `{i}` has incorrect time: Expected {expectedTimeSlot} but got {actualTimeSlot}!")

                        # Check if the associated task matches
                        if expectedTimeSlot.task is None:
                            self.assertIsNone(actualTimeSlot.task, f"Actual TimeSlot should have no task attached to it for a free slot, but instead had {actualTimeSlot.task}.")
                        else:
                            self.assertEqual(expectedTimeSlot.task, actualTimeSlot.task, f"The wrong task was allocated to this TimeSlot! Should have been {expectedTimeSlot.task} but instead was {actualTimeSlot.task}")




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
                taskNo = 0
                for taskDict in paramDict["tasks"]:
                    taskNo += 1
                    task = Task(util.generateUUID(), f"Task #{taskNo}", taskDict["time"], taskDict["time"], taskDict["priority"], deadline, 0)
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
            {"name": "iSSDD-1.0T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": None},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.1T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.2F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("02.01.2099 18:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.3T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("04.01.2099 15:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.4T", "solution": True, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.7, "deadline": arrow.get("01.01.2099 15:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": None},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("01.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-1.5F", "solution": False, "days": defaultDays.copy(), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.9, "deadline": arrow.get("01.01.2099 15:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 1.0, "deadline": None},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("01.01.2099 11:00", "DD.MM.YYYY HH:mm")},
                ]
            }
        ]

        for paramDict in paramDictLst:
            with self.subTest(name=paramDict["name"]):
                tasks = []
                taskNo = 0
                for taskDict in paramDict["tasks"]:
                    taskNo += 1
                    task = Task(util.generateUUID(), f"Task #{taskNo}", taskDict["time"], taskDict["time"], taskDict["priority"], taskDict["deadline"], 0)
                    task.addCompletionTime(taskDict["progress"] * taskDict["time"])
                    tasks.append(task)
                
                days = paramDict["days"]

                debug = False
                result = schedule_alg.isSolvable(tasks, days, arrow.Arrow.fromdate(days[0].date), debug=debug)
                self.assertEqual(result, paramDict["solution"])