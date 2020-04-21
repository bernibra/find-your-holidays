import datetime, calendar

#Global variable
max_hours = 9

# Defining classes for days, months and year
class day(object):
    def __init__(self, d = None):
        self.id = d
        self.previous = d-datetime.timedelta(1)
        self.following = d+datetime.timedelta(1)
        self.day = d.strftime("%A")
        self.weekend = d.strftime("%A")=='Saturday' or d.strftime("%A")=='Sunday'
        self.public_holiday = False
        self.fake_holiday = False
        self.holiday = None
        if self.weekend:
            self.hworked = 0
            self.maxh = 0
        else:
            self.hworked = max_hours
            self.maxh = max_hours
    
class month(object):
    def __init__(self, y = None, m = None):
        self.year = y
        self.id = m
        self.name = calendar.month_name[m]
        self.num_days = calendar.monthrange(y, m)[1]
        self.days = dict()
        for d in range(1, self.num_days+1):
            self.days[datetime.date(y, m, d)] = day(d = datetime.date(y, m, d))

    def add_public_holiday(self, d, name, hours_worked):
        if not self.days[datetime.date(self.year, self.id, d)].weekend:
            self.days[datetime.date(self.year, self.id, d)].public_holiday = True
            self.days[datetime.date(self.year, self.id, d)].holiday = name
            self.days[datetime.date(self.year, self.id, d)].hworked = hours_worked
            self.days[datetime.date(self.year, self.id, d)].maxh = hours_worked
        
    def add_fake_holiday(self):
        pass

    def hours_worked(self):
        hworked = 0
        for d in self.days:
            hworked += self.days[d].hworked
        return hworked

class year(object):
    def __init__(self, y = None):
        self.year = y
        self.months = dict()
        self.days = dict()

    def add_month(self, m = 1):
        self.months[m] = month(y = self.year, m = m)
        self.days.update( self.months[m].days )
    
    def add_public_holiday(self, m, d, name = None, hours_worked=0):
        self.months[m].add_public_holiday(d, name=name, hours_worked=hours_worked)
        
    def add_long_weekend(self, m, extra):
        self.months[m].add_fake_holiday(d)
        
    def add_long_weekend(self, m, start, ndays, maxh):
        self.months[m].add_fake_holiday(d)
        
    def hours_worked(self):
        hworked = 0
        for m in self.months:
            hworked += self.months[m].hours_worked()
        return hworked
