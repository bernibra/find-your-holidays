#from icalendar import Calendar, Event
#from datetime import timedelta, datetime
#import pytz, sys
#import pandas as pd
import datatype
import pandas as pd
import random
import datetime, calendar



def add_holidays_google(file="./data/raw/holidays/holidays.csv"):
    # I should create api google calendar and a calendar to manage people's holidays. This function should add the public holidays from file "file". Then people should manually add holidays there using the right id or holiday "name".
    pass

def read_holidays_google(file="./data/raw/holidays/holidays.csv"):
    # I should create api google calendar and a calendar to manage people's holidays. This function should read the holidays from google calendars' api, including the public and personal holidays.
    pass

def read_holidays_csv(file="./data/raw/holidays/holidays.csv"):
    # Read csv with public holidays
    f = open(file, "r+")
    lines = [x.strip().split(",") for x in f.readlines()]
    f.close()
    return lines
    
def read_target(file="./data/raw/timesheet/targets.csv"):
    # Read csv with public holidays
    f = open(file, "r+")
    lines = [x.strip().split(",") for x in f.readlines()]
    lines = dict([(x[0], float(x[1])) for x in lines])
    f.close()
    return lines

def modify_xlsx(file="./data/raw/timesheet/ETH_Timesheet_2020_Bernat.xlsx"):
    # I should create a function that takes the xlsx file and modify the right entry... but I think this is pretty fucking hard while mantaining the format... At the moment, I will skip this and only provide a csv file.
    pass

def create_year(year=2020):
    # Create year object
    data = datatype.year(2020)
    for i in range(1,13):
        data.add_month(i)
    
    # Load essential data
    holidays = read_holidays_csv()
    #target_ = read_target()

    # Add public holidays
    for i in holidays:
        d, m, y = i[0].split(".")
        name = i[2]
        hw = float(i[3])
        data.add_public_holiday(m = int(m), d = int(d), name = name, hours_worked = hw)
 
    for i in data.months:
        target = dict([(data.months[i].name, round(data.months[i].max_hours(), 2)) for i in range(1,13)])
     
    return data

def generate_table_holidays(data):
    sorted_days = list(data.days.keys())
    sorted_days.sort()
    results = []
    for i in sorted_days:
        if data.days[i].fake_holiday:
            results += [i, "holiday"]
        elif data.days[i].public_holiday:
            results += [i, "public holiday"]
    return results
    
def fill_work_hours(data, minh=4.1, maxh=9.2):
    for i in data.months:
        for j in data.months[i].days:
            if not data.months[i].days[j].weekend and not data.months[i].days[j].fake_holiday:
                if minh<=data.months[i].days[j].maxh:
                    data.months[i].days[j].hworked = round(minh,2)
                else:
                    data.months[i].days[j].hworked = round(data.months[i].days[j].maxh,2)
    for i in data.months:
        days = list(data.months[i].days.keys())
        target = round(data.months[i].max_hours(), 2)
        for j in list(data.months[i].days.keys()):
            target -= data.months[i].days[j].hworked
        
        target = target - data.months[i].holiday_hours()
        N = len(data.months[i].days)-1
        j = 0
        k = 0
        d = float(0.05)
        max_k = int(target/0.05)*100
        while j < int(target/0.05) and k<max_k:
            r = random.randint(0, N)
            k += 1
            if data.months[i].days[days[r]].fake_holiday:
                continue
            if data.months[i].days[days[r]].public_holiday and data.months[i].days[days[r]].hworked < data.months[i].days[days[r]].maxh:
                data.months[i].days[days[r]].hworked = round(data.months[i].days[days[r]].hworked + d,2)
                j += 1
            elif not data.months[i].days[days[r]].weekend and not data.months[i].days[days[r]].public_holiday:
                if data.months[i].days[days[r]].hworked < maxh:
                    data.months[i].days[days[r]].hworked = round(data.months[i].days[days[r]].hworked + d,2)
                    j += 1
                    
    return data

def generate_table_results(data):
    data = fill_work_hours(data)
    k = data.year
    output = [",".join([",".join(["",data.months[x].name,"","",""]) for x in data.months])]
    output += [",".join([",".join(["date","h_worked","h_holidays","",""])]*len(data.months))]
    
    for j in range(1, 32):
        z = []
        for i in range(1,13):
            try:
                day = datetime.date(k, i, j)
                x = data.days[day]
                z_ = ",".join([str(day),str(data.days[day].hworked),str(data.days[day].hholidays), "",""])
            except ValueError:
                z_ = ",".join(["","","","",""])
            z += [z_]
        output += [",".join(z)]
        
    """with open('./csvfile.csv','wb') as file:
        for line in output:
            file.write(line)
            file.write('\n')"""
    return "\n".join(output)

"""
# arguments
input_file = sys.argv[1]
output_file = sys.argv[2]
time = sys.argv[3]

# read fixtures calculated by R
df = pd.read_csv(input_file)

# create calendar component
cal = Calendar()
cal.add('proid', 'Stouffer/Tylianakis meetings')
cal.add('version', '2.0')

# function to add simple event subcomponents
def add_event(the_calendar, event_name, start, end):
    event = Event()
    event.add('summary', event_name)
    event.add('dtstart', start)
    event.add('dtend', end)
    the_calendar.add_component(event)
    return

# cycle through each meeting and add event to the calendar
for index ,row in df.iterrows():
    start = row['date'] + " " + time
    start = datetime.strptime(start, '%Y-%m-%d %X')
    start = start.replace(tzinfo = pytz.timezone("Pacific/Auckland"))
    end = start + timedelta(hours = 1)
    add_event(cal, row['person'], start, end)

f = open(output_file, 'wb')
f.write(cal.to_ical())
f.close()
"""
