from customtime import Time
from timeslot import TimeSlot
import uuid
import arrow

def dateString(datetime, time=False):
    if time:
        return f"{datetime.day:02}.{datetime.month:02}.{datetime.year} {datetime.hour:02}:{datetime.minute:02}"
    else:
        return f"{datetime.day:02}.{datetime.month:02}.{datetime.year}"

def timeParse(timeString: str) -> Time:
    hours = int(timeString.split(":")[0])
    minutes = int(timeString.split(":")[1])
    return Time(hours, minutes)

def timeParseAsTuple(timeString: str) -> (int, int):
    hours = int(timeString.split(":")[0])
    minutes = int(timeString.split(":")[1])
    return hours, minutes

def dateTimeStringToArrow(dateString: str) -> arrow.Arrow:
    return arrow.get(dateString, "DD.MM.YYYY HH:mm")

def dateStringToArrow(dateString: str) -> arrow.Arrow:
    return arrow.get(dateString, "DD.MM.YYYY")

def smoothCurrentArrow() -> arrow.Arrow:
    currentArrow = arrow.now()
    currentArrow.second = 0
    currentArrow.microsecond = 0

    if currentArrow.minute >= 30:
        hour = currentArrow.hour + 1
        minute = 0
    else:
        hour = currentArrow.hour
        minute = 30

    return arrow.Arrow(currentArrow.year, currentArrow.month, currentArrow.day, hour=hour, minute=minute, second=0, microsecond=0)

# DO NOT CHANGE THESE. Many Tests depend on them!
def exampleTimeSlots() -> [TimeSlot]:
    return [TimeSlot(Time(8, 30), Time(12, 30)), TimeSlot(Time(13, 00), Time(17, 00))]

def generateUUID() -> str:
    return str(uuid.uuid4())

def arrowToTime(a: arrow.Arrow) -> Time:
    return Time(a.hour, a.minute)

def formatDate(a: arrow.Arrow, time=True) -> str:
    if time:
        return a.strftime("%d.%m.%Y %H:%M")
    else:
        return a.strftime("%d.%m.%Y")

def getInfinityDate() -> arrow.Arrow:
    return arrow.get("31.12.3999 00:00", "DD.MM.YYYY HH:mm")