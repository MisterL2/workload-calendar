from unittest import TestCase
from task import Task
from priority_alg import *
import arrow

farAwayDeadline = arrow.get("01.01.2099 23:59", "DD.MM.YYYY HH:mm")

class AlgTest(TestCase):
    def test_basic(self):
        task1 = Task("Task #1", 10, 10, 2, farAwayDeadline, 30)
        task2 = Task("Task #2", 10, 10, 3, farAwayDeadline, 30)
        
        self.assertEqual(task2, prioritiseTaskHappy(task1, task2))

        task3 = Task("Task #3", 10, 10, 8, farAwayDeadline, 30)
        task4 = Task("Task #4", 10, 10, 6, farAwayDeadline, 30)
        
        self.assertEqual(task3, prioritiseTaskHappy(task3, task4))

        task5 = Task("Task #5", 10, 10, 7, farAwayDeadline, 30)
        task6 = Task("Task #6", 10, 10, 7, farAwayDeadline, 30)
        
        # When they are equal, the "larger" name should get selected
        self.assertEqual(task6, prioritiseTaskHappy(task5, task6))
        self.assertEqual(task6, prioritiseTaskHappy(task6, task5))

    def test_B(self):
        testParameterDictLst = [
            {"name": "B0.1", "prio1" :2, "prio2": 9, "progress": 0.9, "correctTask": 1},
            {"name": "B0.2", "prio1" :3, "prio2": 8, "progress": 0.9, "correctTask": 1},
            {"name": "B0.3", "prio1" :4, "prio2": 7, "progress": 0.9, "correctTask": 1},
            {"name": "B0.4", "prio1" :5, "prio2": 6, "progress": 0.9, "correctTask": 1},
            {"name": "B1.1", "prio1" :2, "prio2": 9, "progress": 0.8, "correctTask": 2},
            {"name": "B1.2", "prio1" :3, "prio2": 8, "progress": 0.8, "correctTask": 1},
            {"name": "B1.3", "prio1" :4, "prio2": 7, "progress": 0.8, "correctTask": 1},
            {"name": "B1.4", "prio1" :5, "prio2": 6, "progress": 0.8, "correctTask": 1},
            {"name": "B2.1", "prio1" :2, "prio2": 9, "progress": 0.7, "correctTask": 2},
            {"name": "B2.2", "prio1" :3, "prio2": 8, "progress": 0.7, "correctTask": 2},
            {"name": "B2.3", "prio1" :4, "prio2": 7, "progress": 0.7, "correctTask": 1},
            {"name": "B2.4", "prio1" :5, "prio2": 6, "progress": 0.7, "correctTask": 1},
            {"name": "B3.1", "prio1" :2, "prio2": 9, "progress": 0.6, "correctTask": 2},
            {"name": "B3.2", "prio1" :3, "prio2": 8, "progress": 0.6, "correctTask": 2},
            {"name": "B3.3", "prio1" :4, "prio2": 7, "progress": 0.6, "correctTask": 2},
            {"name": "B3.4", "prio1" :5, "prio2": 6, "progress": 0.6, "correctTask": 1},
            {"name": "B4.1", "prio1" :2, "prio2": 9, "progress": 0.5, "correctTask": 2},
            {"name": "B4.2", "prio1" :3, "prio2": 8, "progress": 0.5, "correctTask": 2},
            {"name": "B4.3", "prio1" :4, "prio2": 7, "progress": 0.5, "correctTask": 2},
            {"name": "B4.4", "prio1" :5, "prio2": 6, "progress": 0.5, "correctTask": 1},
            {"name": "B5.1", "prio1" :2, "prio2": 9, "progress": 0.4, "correctTask": 2},
            {"name": "B5.2", "prio1" :3, "prio2": 8, "progress": 0.4, "correctTask": 2},
            {"name": "B5.3", "prio1" :4, "prio2": 7, "progress": 0.4, "correctTask": 2},
            {"name": "B5.4", "prio1" :5, "prio2": 6, "progress": 0.4, "correctTask": 1},
            {"name": "B6.1", "prio1" :2, "prio2": 9, "progress": 0.3, "correctTask": 2},
            {"name": "B6.2", "prio1" :3, "prio2": 8, "progress": 0.3, "correctTask": 2},
            {"name": "B6.3", "prio1" :4, "prio2": 7, "progress": 0.3, "correctTask": 2},
            {"name": "B6.4", "prio1" :5, "prio2": 6, "progress": 0.3, "correctTask": 1},
            {"name": "B7.1", "prio1" :2, "prio2": 9, "progress": 0.2, "correctTask": 2},
            {"name": "B7.2", "prio1" :3, "prio2": 8, "progress": 0.2, "correctTask": 2},
            {"name": "B7.3", "prio1" :4, "prio2": 7, "progress": 0.2, "correctTask": 2},
            {"name": "B7.4", "prio1" :5, "prio2": 6, "progress": 0.2, "correctTask": 2},
            {"name": "B8.1", "prio1" :2, "prio2": 9, "progress": 0.1, "correctTask": 2},
            {"name": "B8.2", "prio1" :3, "prio2": 8, "progress": 0.1, "correctTask": 2},
            {"name": "B8.3", "prio1" :4, "prio2": 7, "progress": 0.1, "correctTask": 2},
            {"name": "B8.4", "prio1" :5, "prio2": 6, "progress": 0.1, "correctTask": 2},
        ]
        missingTests = 0
        for testParamDict in testParameterDictLst:
            with self.subTest(name=testParamDict["name"]):
                if testParamDict["correctTask"] == "TBD":
                    missingTests += 1
                    continue # Test not finished yet

                task1 = Task("Task #1", 10, 10, testParamDict["prio1"], farAwayDeadline, 30)
                task1.updateValue("completedTime", 10 * testParamDict["progress"]) # Using this command to avoid the user-prompt ("Did you complete the task?")
                task2 = Task("Task #2", 10, 10, testParamDict["prio2"], farAwayDeadline, 30)

                chosenTask = prioritiseTaskHappy(task1, task2)
                correctTask = testParamDict["correctTask"]
                progressPercentage = f"{testParamDict['progress']*100:3}%"
                if correctTask == 1:
                    self.assertEqual(task1, chosenTask, f"\nShould have selected Task #1 (prio: {testParamDict['prio1']}, progress: {progressPercentage}) instead of Task #1 (prio: {testParamDict['prio2']}, progress: 0%)")
                elif correctTask == 2:
                    self.assertEqual(task2, chosenTask, f"\nShould have selected Task #2 (prio: {testParamDict['prio2']}, progress: 0%) instead of Task #1 (prio: {testParamDict['prio1']}, progress: {progressPercentage})")
                else:
                    raise Exception(f"Invalid value for 'correctTask': {correctTask}")

        self.assertEqual(missingTests, 0, f"Not all tests for this category were implemented yet. {len(testParameterDictLst) - missingTests}/{len(testParameterDictLst)} Tests implemented")


        