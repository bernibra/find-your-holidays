#from icalendar import Calendar, Event
#from datetime import timedelta, datetime
#import pytz, sys
#import pandas as pd
import datatype

def add_holidays_google(file="../data/raw/holidays/holidays.csv"):
    # I should create api google calendar and a calendar to manage people's holidays. This function should add the public holidays from file "file". Then people should manually add holidays there using the right id or holiday "name".
    pass

def read_holidays_google(file="../data/raw/holidays/holidays.csv"):
    # I should create api google calendar and a calendar to manage people's holidays. This function should read the holidays from google calendars' api, including the public and personal holidays.
    pass

def read_holidays_csv(file="../data/raw/holidays/holidays.csv"):
    # Read csv with public holidays
    f = open(file, "r+")
    lines = [x.strip().split(",") for x in f.readlines()]
    f.close()
    return lines
    
def read_target(file="../data/raw/timesheet/targets.csv"):
    # Read csv with public holidays
    f = open(file, "r+")
    lines = [x.strip().split(",") for x in f.readlines()]
    lines = dict([(x[0], float(x[1])) for x in lines])
    f.close()
    return lines

def modify_xlsx(file="../data/raw/timesheet/ETH_Timesheet_2020_Bernat.xlsx"):
    # I should create a function that takes the xlsx file and modify the right entry... but I think this is pretty fucking hard while mantaining the format... At the moment, I will skip this and only provide a csv file.
    pass

def create_year(year=2020):
    # Create year object
    data = datatype.year(2020)
    for i in range(1,13):
        data.add_month(i)
    
    # Load essential data
    holidays = read_holidays_csv()
    target_ = read_target()

    # Add public holidays
    for i in holidays:
        d, m, y = i[0].split(".")
        name = i[2]
        hw = float(i[3])
        data.add_public_holiday(m = int(m), d = int(d), name = name, hours_worked = hw)
 
    for i in data.months:
        target = dict([(data.months[i].name, round(data.months[i].max_hours(), 2)) for i in range(1,13)])
     
    return data, holidays


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
