from unittest import TestCase
from task import Task
from day import Day
from timeslot import TimeSlot
from appointment import Appointment
from schedule import Schedule
import arrow
import util
import schedule_alg

class ScheduleTest(TestCase):
    def test_calculate_Easy_HappySchedule(self): # cEHS
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        lastWorkConfirmed = arrow.get("03.05.2080", "DD.MM.YYYY")
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]
        appointmentDays = [day.copy() for day in defaultDays]
        appointments = [
            Appointment("App #1 - Normal", TimeSlot.fromString("10:00 - 11:15")),
            Appointment("App #2 - Normal", TimeSlot.fromString("14:00 - 15:00")),
            Appointment("App #3 - Overshoots start", TimeSlot.fromString("06:00 - 09:30")),
            Appointment("App #4 - Overshoots end", TimeSlot.fromString("16:00 - 19:30")),
            Appointment("App #5 - Goes over lunch", TimeSlot.fromString("11:30 - 13:30")),
            Appointment("App #6 - Goes over entire day", TimeSlot.fromString("06:30 - 21:00"))
        ]

        appointmentDays[0].addAppointment(appointments[0])
        appointmentDays[0].addAppointment(appointments[1])
        appointmentDays[1].addAppointment(appointments[2])
        appointmentDays[1].addAppointment(appointments[3])
        appointmentDays[2].addAppointment(appointments[4])
        appointmentDays[3].addAppointment(appointments[5])

        paramDictLst = [
            {"name": "cEHS-0.1a", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # Default case; easy deadlines, just schedule due to priority
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
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
                            {"timeslotString": "13:00 - 14:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("07.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            
                            
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.1b", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # Default case; no deadlines, just schedule due to priority
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": None, "minBlock": 0},
                    {"taskName": "Task #2", "time": 1200, "priority": 8, "progress": 0, "deadline": None, "minBlock": 0},
                    {"taskName": "Task #3", "time": 900, "priority": 6, "progress": 0, "deadline": None, "minBlock": 0},
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
                            
                        ]
                    },
                    {"date": arrow.get("07.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            
                            
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.2", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # Lowest priority date has a fairly tight deadline and needs to be scheduled first. One date also has a non-zero progress
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 11:00", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1200, "priority": 8, "progress": 0.5, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 10:30", "taskName": "Task #1"},
                            {"timeslotString": "10:30 - 12:30", "taskName": "Task #2"},
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
                        ]
                    },
                    {"date": arrow.get("06.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            
                            
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.3", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # The low priority task has a moderately tight deadline that either of the higher priority tasks could fill
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("02.01.2099 14:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1000, "priority": 8, "progress": 0.8, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 200, "priority": 6, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 11:50", "taskName": "Task #2"},
                            {"timeslotString": "11:50 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 14:20", "taskName": "Task #1"},
                            {"timeslotString": "14:20 - 17:00", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 09:10", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.4", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # The low priority task has a moderately tight deadline that only the less-significant of the two higher-priority tasks can fill
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("02.01.2099 14:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1000, "priority": 8, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 160, "priority": 6, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 11:10", "taskName": "Task #3"},
                            {"timeslotString": "11:10 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 13:40", "taskName": "Task #1"},
                            {"timeslotString": "13:40 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 14:20", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("05.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            
                            
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.5", "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), # A very high priority no-deadline task should be scheduled first, then the two identical-deadline tasks in order of SIGNIFICANCE (prio-6 task has higher significance due to progress) and then the other late-deadline one. Also there are non-zero progress values.
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 4, "progress": 0, "deadline": arrow.get("02.01.2099 14:35", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1200, "priority": 6, "progress": 0.5, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 200, "priority": 7, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #4", "time": 215, "priority": 10, "progress": 0, "deadline": None, "minBlock": 0}
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:05", "taskName": "Task #4"},
                            {"timeslotString": "12:05 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 14:35", "taskName": "Task #1"},
                            {"timeslotString": "14:35 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 16:35", "taskName": "Task #2"},
                            {"timeslotString": "16:35 - 17:00", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 11:25", "taskName": "Task #3"}
                        ]
                    },
                    {"date": arrow.get("05.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.6", "schedule": Schedule([day.copy() for day in appointmentDays], lastWorkConfirmed), # Only appointments
                "tasks": [
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[0].timeSlot.timeString, "taskName": appointments[0].name},
                            {"timeslotString": appointments[1].timeSlot.timeString, "taskName": appointments[1].name},
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[2].timeSlot.timeString, "taskName": appointments[2].name},
                            {"timeslotString": appointments[3].timeSlot.timeString, "taskName": appointments[3].name}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[4].timeSlot.timeString, "taskName": appointments[4].name},
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[5].timeSlot.timeString, "taskName": appointments[5].name},
                        ]
                    },
                    {"date": arrow.get("05.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                        ]
                    }
                ]
            },


            {"name": "cEHS-0.7", "schedule": Schedule([day.copy() for day in appointmentDays], lastWorkConfirmed), # Similar to cEHS-0.5, but with a different list of days (containing appointments)
                "tasks": [
                    {"taskName": "Task #1", "time": 600, "priority": 4, "progress": 0, "deadline": arrow.get("03.01.2099 11:00", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #2", "time": 1200, "priority": 6, "progress": 0.5, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #3", "time": 200, "priority": 7, "progress": 0, "deadline": arrow.get("10.01.2099 12:30", "DD.MM.YYYY HH:mm"), "minBlock": 0},
                    {"taskName": "Task #4", "time": 215, "priority": 10, "progress": 0, "deadline": None, "minBlock": 0}
                ],
                "expected" : [
                    {"date": arrow.get("01.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 10:00", "taskName": "Task #4"},
                            {"timeslotString": appointments[0].timeSlot.timeString, "taskName": appointments[0].name},
                            {"timeslotString": "11:15 - 12:30", "taskName": "Task #4"},
                            {"timeslotString": "13:00 - 13:50", "taskName": "Task #4"},
                            {"timeslotString": "13:50 - 14:00", "taskName": "Task #1"},
                            {"timeslotString": appointments[1].timeSlot.timeString, "taskName": appointments[1].name},
                            {"timeslotString": "15:00 - 17:00", "taskName": "Task #1"}
                        ]
                    },
                    {"date": arrow.get("02.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[2].timeSlot.timeString, "taskName": appointments[2].name},
                            {"timeslotString": "09:30 - 12:30", "taskName": "Task #1"},
                            {"timeslotString": "13:00 - 16:00", "taskName": "Task #1"},
                            {"timeslotString": appointments[3].timeSlot.timeString, "taskName": appointments[3].name}
                        ]
                    },
                    {"date": arrow.get("03.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 10:20", "taskName": "Task #1"},
                            {"timeslotString": "10:20 - 11:30", "taskName": "Task #2"},
                            {"timeslotString": appointments[4].timeSlot.timeString, "taskName": appointments[4].name},
                            {"timeslotString": "13:30 - 17:00", "taskName": "Task #2"}
                        ]
                    },
                    {"date": arrow.get("04.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": appointments[5].timeSlot.timeString, "taskName": appointments[5].name},
                        ]
                    },
                    {"date": arrow.get("05.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 12:30", "taskName": "Task #2"},
                            {"timeslotString": "13:00 - 14:20", "taskName": "Task #2"},
                            {"timeslotString": "14:20 - 17:00", "taskName": "Task #3"}
                            
                        ]
                    },
                    {"date": arrow.get("06.01.2099", "DD.MM.YYYY").date(),
                        "timeslots": [
                            {"timeslotString": "08:30 - 09:10", "taskName": "Task #3"}
                        ]
                    }
                ]
            }
         
        ]

        for paramDict in paramDictLst:
            with self.subTest(name=paramDict["name"]):
                print(paramDict["name"])
                tasks = []
                for taskDict in paramDict["tasks"]:
                    task = Task(util.generateUUID(), taskDict["taskName"], taskDict["time"], taskDict["time"], taskDict["priority"], taskDict["deadline"], taskDict["minBlock"])
                    task.addCompletionTime(taskDict["progress"] * taskDict["time"])
                    tasks.append(task)
                
                schedule = paramDict["schedule"]

                debug = paramDict["name"] == "cEHS-0.8"

                schedule = schedule_alg.calculateSchedule(tasks, schedule, arrow.Arrow.fromdate(schedule.days()[0].date), debug=debug)

                if debug: print(tasks)
                if debug: print(schedule)

                for solutionDict in paramDict["expected"]: # Go through each expected day and see if the timeslots are assigned correctly
                    actualDay = schedule.getDay(solutionDict["date"])
                    expectedTimeSlots = []
                    for expectedTimeSlotDict in solutionDict["timeslots"]:
                        ts = TimeSlot.fromString(expectedTimeSlotDict["timeslotString"])

                        # If there is a task name specified, attach the task to the expectedTimeSlot
                        taskName = expectedTimeSlotDict["taskName"]
                        if taskName is not None:
                            for app in appointments:
                                if taskName == app.name:
                                    ts.taskOrAppointment = app
                                    break
                            else:
                                # Otherwise find the task with the correct taskName
                                for task in tasks:
                                    if task.name == taskName:
                                        ts.taskOrAppointment = task
                                        break
                        
                        expectedTimeSlots.append(ts)

                    amtExpected = len(expectedTimeSlots)
                    amtActual = len(actualDay.daySchedule)

                    if debug: print(actualDay.display())

                    self.assertEqual(amtExpected, amtActual, f"Incorrect length of TimeSlots: Expected {amtExpected} but got {amtActual}!")
                    for i in range(amtExpected):
                        expectedTimeSlot = expectedTimeSlots[i]
                        actualTimeSlot = actualDay.daySchedule[i]
                        # Check if the TimeSlots are equal (This only checks if their times are equal. It does not consider the associated task)
                        self.assertEqual(expectedTimeSlot, actualTimeSlot, f"TimeSlot with index `{i}` has incorrect time: Expected {expectedTimeSlot} but got {actualTimeSlot}!")

                        # Check if the associated task matches
                        if expectedTimeSlot.taskOrAppointment is None:
                            self.assertIsNone(actualTimeSlot.taskOrAppointment, f"Actual TimeSlot should have no task attached to it for a free slot, but instead had {actualTimeSlot.taskOrAppointment}.")
                        else:
                            self.assertEqual(expectedTimeSlot.taskOrAppointment, actualTimeSlot.taskOrAppointment, f"The wrong task was allocated to this TimeSlot! Should have been {expectedTimeSlot.taskOrAppointment} but instead was {actualTimeSlot.taskOrAppointment}")




    def test_isSolvable_Standard_AllSameDeadline(self): # iSSASD
        deadline = arrow.get("31.01.2099", "DD.MM.YYYY")
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]
        lastWorkConfirmed = arrow.get("03.05.2080", "DD.MM.YYYY")

        paramDictLst = [
            {"name": "iSSASD-0.1T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.8},
                {"time": 1200, "priority": 8, "progress": 0},
                {"time": 900, "priority": 6, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.2T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0},
                {"time": 600, "priority": 5, "progress": 0.4},
                {"time": 600, "priority": 7, "progress": 0.1},
                ]
            },
            {"name": "iSSASD-0.3T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0},
                {"time": 2400, "priority": 7, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.4F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0},
                {"time": 2401, "priority": 7, "progress": 0},
                ]
            },
            {"name": "iSSASD-0.5F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 12000, "priority": 5, "progress": 0}
                ]
            },
            {"name": "iSSASD-0.6T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 6000, "priority": 2, "progress": 0},
                {"time": 6000, "priority": 5, "progress": 0.5}, # So 3000 remaining
                {"time": 6000, "priority": 7, "progress": 0.8}, # So 1200 remaining
                ]
            },
            {"name": "iSSASD-0.7F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
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
                
                schedule = paramDict["schedule"]

                debug = False
                result = schedule_alg.isSolvable(tasks, schedule.days(), arrow.Arrow.fromdate(schedule.days()[0].date), debug=debug)
                self.assertEqual(result, paramDict["solution"])

    def test_isSolvable_Standard_DifferentDeadline(self): # iSSDD
        dates = [arrow.get(f"{i:02}.01.2099", "DD.MM.YYYY").date() for i in range(1, 31)] # 01.01 - 30.01; 240h total
        defaultDays = [Day(d, util.exampleTimeSlots(), [], special=True) for d in dates]
        lastWorkConfirmed = arrow.get("03.05.2080", "DD.MM.YYYY")

        paramDictLst = [
            {"name": "iSSDD-0.1T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("02.01.2099 10:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.2F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 09:00", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.3T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("05.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("06.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("07.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.4T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 04:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("09.01.2099 00:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 12:45", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.5F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("03.01.2099 04:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("09.01.2099 00:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("04.01.2099 07:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.6T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.5, "deadline": arrow.get("02.01.2099 16:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:15", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0, "deadline": arrow.get("08.01.2099 23:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.7F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": arrow.get("02.01.2099 15:45", "DD.MM.YYYY HH:mm")},
                {"time": 900, "priority": 6, "progress": 0.2, "deadline": arrow.get("04.01.2099 23:15", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.8T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 14:00", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("03.01.2099 16:00", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-0.9F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("10.01.2099 09:30", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("03.01.2099 14:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-1.0T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": None},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.1T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 15:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.2F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": None},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("02.01.2099 18:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.3T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0, "deadline": arrow.get("04.01.2099 15:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0, "deadline": arrow.get("03.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                {"time": 180, "priority": 6, "progress": 0, "deadline": None},
                ]
            },
            {"name": "iSSDD-1.4T", "solution": True, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
                {"time": 600, "priority": 2, "progress": 0.7, "deadline": arrow.get("01.01.2099 15:00", "DD.MM.YYYY HH:mm")},
                {"time": 1200, "priority": 8, "progress": 0.5, "deadline": None},
                {"time": 180, "priority": 6, "progress": 0, "deadline": arrow.get("01.01.2099 12:30", "DD.MM.YYYY HH:mm")},
                ]
            },
            {"name": "iSSDD-1.5F", "solution": False, "schedule": Schedule([day.copy() for day in defaultDays], lastWorkConfirmed), "tasks": [
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
                
                schedule = paramDict["schedule"]

                debug = False
                result = schedule_alg.isSolvable(tasks, schedule.days(), arrow.Arrow.fromdate(schedule.days()[0].date), debug=debug)
                self.assertEqual(result, paramDict["solution"])