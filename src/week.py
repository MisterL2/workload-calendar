from day import Day

class Week():
    def __init__(self, days: [Day]):
        self.days = days

    def __repr__(self) -> str:
        headline = f"Week ({self.days[0].dateString} - {self.days[-1].dateString}) {sum([day.dayScheduleWorkTime for day in self.days])/60:.1f} h\n"
        return headline + "\n".join([day.detailedView() for day in self.days])