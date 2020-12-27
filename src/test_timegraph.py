from unittest import TestCase
from timegraph import TimeGraph

class TimeGraphTest(TestCase):
    def test_noOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 2000, 500) # 1500 - 2000
        tg.addTimeInterval("middle", 1000, 250) # 750 - 1000

        # Expected result: 200[first]500  750[middle]1000  1500[last]2000

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 200, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 500, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 750, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 1000, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "middle", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 1500, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 2000, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_overlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 1000, 300) # 700 - 1000
        tg.addTimeInterval("middle", 800, 200) # 600 - 800

        # Expected result: 200[first]500[middle]700[last]1000

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 200, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 500, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 500, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 700, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "middle", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 700, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1000, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_equalOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 1000, 300) # 700 - 1000
        tg.addTimeInterval("middle", 1000, 200) # 800 - 1000

        # Expected result: 200[first]500[middle]800[last]1000

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 200, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 500, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 500, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 700, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "middle", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 700, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1000, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_equalOverlap2(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 1000, 200) # 800 - 1000
        tg.addTimeInterval("middle", 1000, 300) # 700 - 1000

        # Expected result: 200[first]500[middle]800[last]1000

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 200, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 500, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 500, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 800, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "middle", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 800, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1000, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_complexMultiOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 1000, 300) # 700 - 1000
        tg.addTimeInterval("middle", 800, 400) # 400 - 800

        # Expected result: 0[first]300[middle]700[last]1000

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 0, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 300, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 300, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 700, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "middle", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 700, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1000, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_complexTripleOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("third", 1000, 300) # 700 - 1000
        tg.addTimeInterval("second", 800, 300) # 500 - 800
        tg.addTimeInterval("last", 1050, 100) # 950 - 1050

        # Expected result: 50[first]350[second]650[third]950[last]1050

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 50, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 350, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 350, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 650, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "second", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 650, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 950, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "third", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

        self.assertEqual(tg.timeIntervals[3].startTimeInMinutes, 950, "fourth interval start time wrong")
        self.assertEqual(tg.timeIntervals[3].endTimeInMinutes, 1050, "fourth interval end time wrong")
        self.assertEqual(tg.timeIntervals[3].name, "last", f"Wrong name at fourth interval: {tg.timeIntervals[3].name}")

    def test_IncorporatingOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("second", 1000, 300) # 700 - 1000
        tg.addTimeInterval("last", 1500, 900) # 600 - 1500

        # Expected result: 0[first]300[second]600[last]1500

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 0, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 300, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 300, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 600, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "second", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 600, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1500, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_IncorporatedOverlap(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("last", 1500, 800) # 700 - 1500
        tg.addTimeInterval("second", 1200, 300) # 900 - 1200

        # Expected result: 100[first]400[second]700[last]1500

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 100, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 400, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 400, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 700, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "second", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 700, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1500, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "last", f"Wrong name at third interval: {tg.timeIntervals[2].name}")

    def test_impossibleOverlapException(self):
        tg = TimeGraph()
        tg.addTimeInterval("first", 500, 300) # 200 - 500
        tg.addTimeInterval("second", 1000, 300) # 700 - 1000

        self.assertRaises(Exception, tg.addTimeInterval, "impossible", 600, 600)
        self.assertRaises(Exception, tg.addTimeInterval, "impossible", 800, 600)
        self.assertRaises(Exception, tg.addTimeInterval, "impossible", 1150, 600)

        tg.addTimeInterval("possible", 1200, 600)

        # Expected 0[first]300[second]600[possible]1200

        self.assertEqual(tg.timeIntervals[0].startTimeInMinutes, 0, "first interval start time wrong")
        self.assertEqual(tg.timeIntervals[0].endTimeInMinutes, 300, "first interval end time wrong")
        self.assertEqual(tg.timeIntervals[0].name, "first", f"Wrong name at first interval: {tg.timeIntervals[0].name}")

        self.assertEqual(tg.timeIntervals[1].startTimeInMinutes, 300, "second interval start time wrong")
        self.assertEqual(tg.timeIntervals[1].endTimeInMinutes, 600, "second interval end time wrong")
        self.assertEqual(tg.timeIntervals[1].name, "second", f"Wrong name at second interval: {tg.timeIntervals[1].name}")

        self.assertEqual(tg.timeIntervals[2].startTimeInMinutes, 600, "third interval start time wrong")
        self.assertEqual(tg.timeIntervals[2].endTimeInMinutes, 1200, "third interval end time wrong")
        self.assertEqual(tg.timeIntervals[2].name, "possible", f"Wrong name at third interval: {tg.timeIntervals[2].name}")