from customtime import Time
import arrow

def dateString(datetime, time=False):
    if time:
        return f"{datetime.day:02}.{datetime.month:02}.{datetime.year} @ {datetime.hour:02}:{datetime.minute:02}"
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
    return arrow.get(dateString,"DD.MM.YYYY @ HH:mm")

def dateStringToArrow(dateString: str) -> arrow.Arrow:
    return arrow.get(dateString,"DD.MM.YYYY")