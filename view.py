from flask import Blueprint, render_template, url_for
import datetime
import time
import requests
import pandas as pd
from math import floor

views = Blueprint("view", __name__)

URL_GET = 'https://api.sheety.co/16665804b02288a8075d4ba075187032/generatorLog/runTime'
URL_POST = 'https://api.sheety.co/16665804b02288a8075d4ba075187032/generatorLog/runtime'
URL_PUT = 'https://api.sheety.co/16665804b02288a8075d4ba075187032/generatorLog/runtime/[Object ID]'
HEADERS = {"Content-Type": "application/json",}

@views.route("/")
def home():
    return render_template(
        "home.html")

@views.route("/write_start", methods=["GET", "POST"])
def write_start():
    start_date = datetime.date.today()
    start_time = datetime.datetime.now().strftime("%H:%M:%S")

    payload = {
        "startDate": f"{start_date}",
        "endDate": '',
        "startTime": f"{start_time}",
        "endTime": ''}
    
    response = requests.post(URL_POST, headers=HEADERS, json={'runtime':payload})

    return render_template(
        "home.html")
    
@views.route("/write_end", methods=["GET", "POST"])
def write_end():
    id = _get_last_id()
    URL = str(URL_PUT.replace('[Object ID]', str(id)))
    end_date = datetime.date.today()
    end_time = datetime.datetime.now().strftime("%H:%M:%S")

    payload = {
        "endDate": f"{end_date}",
        "endTime": f"{end_time}"}
    
    response = requests.put(URL, headers=HEADERS, json={"runtime": payload})
    
    return render_template(
        "home.html")

# schedule viewing page
@views.route("/schedule", methods=["GET"])
def schedule():
    response = requests.get(URL_GET)
    data = response.json()
    print(data)
    data_frame = pd.DataFrame(data['runtime'])
    elapsed_hours = get_elapsed_time(data_frame)
    maintanence_check(runtime = elapsed_hours)
    data_frame = response_to_html(data)

    return render_template(
        "logs.html", data = data_frame.to_html(classes="dataframe",index=False), elapsed = elapsed_hours)

def _get_last_id():
    response = requests.get(URL_GET)
    data = response.json()
    print(data)
    last_entry = data['runtime'][-1]
    id = last_entry['id']

    return id

def get_elapsed_time(df):
    start_time_series = df['startTime'][:]
    end_time_series = df['endTime'][:]
    start_time_list = []
    end_time_list = []

    for time in start_time_series:
        start_time_list.append(time)
    for time in end_time_series:
        end_time_list.append(time)

    start_time = []
    end_time = []

    for time in start_time_list:
        if time == None or str(time) == 'nan':
            start_time.append(datetime.datetime.strptime('0:0:0', "%H:%M:%S").time())
        else:
            start_time.append(datetime.datetime.strptime(str(time), "%H:%M:%S").time())

    for time in end_time_list:
        if time == None or str(time) == 'nan':
            end_time.append(datetime.datetime.strptime('0:0:0', "%H:%M:%S").time())
        else:
            end_time.append(datetime.datetime.strptime(str(time), "%H:%M:%S").time())
    
    duration = []
    for time in range(0, len(end_time)):
        duration.append(datetime.datetime.combine(datetime.date.today(), end_time[time]) - datetime.datetime.combine(datetime.date.today(), start_time[time]))
    
    duration_hours = 0
    for delta in duration:
        duration_hours += delta.seconds / 3600 + delta.days * 24

    return floor(duration_hours)

def response_to_html(data):
    data_frame = pd.DataFrame(data['runtime'])
    data_frame.drop('id', axis=1, inplace=True)
    return data_frame

def maintanence_check(**kwargs):
    runtime = kwargs.get('runtime', 0)

    periodic_maintenance_schedule = {
        'weekly':{ 
            ('OIL CHANGE',
             'CLEAN SPARK PLUG',
             'CLEAN AIR FILTER') : 100,
        },
        'monthly':{
            ('CLEAN SPARK PLUG',
             'CLEAN AIR FILTER') : 100,
            ('REPLACE AIR FILTER',
             'CLEAN FUEL FILTER',
             'CLEAN & ADJUST SPARK PLUG & ELECTRODES') : 200,
        },
        'every 500 hours':{
            ('REPLACE SPARK PLUG',
             'REMOVE CARBON FROM CYLINDER HEAD',
             'CHECK & ADJUST VALVE CLEARANCE',
             'CHECK & ADJUST CARBURETOR',
             'CHECK & REPLACE CARBON BRUSHES') : 500
        },
        'every 1000 hours':{
            'REPLACE FUEL LINES' : 8760,
            ('OVERHAUL ENGINE', 'CHECK ROTOR', 'CHECK STATOR', 'REPLACE ENGINE MOUNT') : 1000,
        }
    }
    weekly_maintanence_required = False
    monthly_maintanence_required = False
    hours_500_maintanence_required = False
    hours_1000_maintanence_required = False

    if runtime >= periodic_maintenance_schedule['weekly'][('OIL CHANGE', 'CLEAN SPARK PLUG', 'CLEAN AIR FILTER')]:
        weekly_maintanence_required = True
    if runtime >= periodic_maintenance_schedule['monthly'][('CLEAN SPARK PLUG', 'CLEAN AIR FILTER')] \
        or runtime >= periodic_maintenance_schedule['monthly'][('REPLACE AIR FILTER', 'CLEAN FUEL FILTER', 'CLEAN & ADJUST SPARK PLUG & ELECTRODES')]:
        monthly_maintanence_required = True