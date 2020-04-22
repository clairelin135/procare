import numpy as np
import datetime
import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class Employee:
    def __init__(self, id, name, age, gender, bodyfat, height, weight, zipcode, department, team, stock_symbol):
        # Personal Data
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.bodyfat = bodyfat
        self.height = height
        self.weight = weight
        self.zipcode = zipcode
        self.department = department
        self.team = team
        self.stock_symbol = stock_symbol

        # User Input
        self.calories_eaten = []
        self.water_consumed = []
        self.mins_workedout = []

        # Chat
        self.nudge_responses = []

        # Sensor - API
        self.num_task_pendings = []
        self.avg_task_delay = []
        self.git_push_time_difference = []
        self.heart_rate = []
        self.weather = []
        self.temperature = []
        self.stock_ytd = []
        self.chat_tone = []

        # Sensor - Hardware
        self.break_durations = []
        self.focustimes = []
        self.ergonomic_risk_rating = []
        self.stand_triggers = []


        # Daily Sensor Readings
        self.entrance_time = []
        self.exit_time = []
        self.traffic = []

        self.git_push_dist_morning = []
        self.git_push_dist_afternoon = []
        self.git_push_dist_evening = []


        self.weather_constant = ["rainy", "overcast", "snowing", "sunny"]
        self.traffic_constant = ["red", "yellow", "green"]
        self.chat_tone_constant = ["Angry", "Happy"]
        
        

    def get_daily_stats(self):
        now = datetime.datetime.now()

        self.entrance_time.append({"time":now, "data":np.random.randint(3,11)})
        self.exit_time.append({"time":now, "data":np.random.randint(15,23)})
        self.traffic.append({"time":now, "data":self.traffic_constant[np.random.randint(0, len(self.traffic_constant))]})

        x = np.random.random()
        y = (1-x) * np.random.random()
        z = 1 - x - y

        self.git_push_dist_morning.append({"time":now, "data":x})
        self.git_push_dist_afternoon.append({"time":now, "data":y})
        self.git_push_dist_evening.append({"time":now, "data":z})

    
    def get_api_stats(self):
        now = datetime.datetime.now()

        self.num_task_pendings.append({"time":now, "data":np.random.randint(0,100)})
        self.avg_task_delay.append({"time":now, "data":np.random.randint(0, 24*60*7)})
        self.git_push_time_difference.append({"time":now, "data":np.random.randint(5, 300)}) # Supposed to get from Git livetime
        self.heart_rate.append({"time":now, "data":np.random.randint(60,180)})
        self.temperature.append({"time":now, "data":np.random.randint(50, 70)}) # Replace with Weather API
        self.stock_ytd.append({"time":now, "data":np.random.random() * (-1 * np.random.randint(0,2))})  # Replace this with Yahoo Finance API
        self.chat_tone.append({"time":now, "data":self.chat_tone_constant[np.random.randint(0, len(self.chat_tone_constant))]})
        self.weather.append({"time":now, "data":self.weather_constant[np.random.randint(0, len(self.weather_constant))]})


    # This is simulated to run every 15 minutes
    def run_sensors(self):
        now = datetime.datetime.now()

        self.break_durations.append({"time":now, "data": [np.random.randint(0,2) for _ in range(15)]})
        self.focustimes.append({"time":now, "data": [np.random.randint(0,2) for _ in range(15)]})
        self.ergonomic_risk_rating.append({"time":now, "data": [np.random.random() * 10 for _ in range(15)]})
        self.stand_triggers.append({"time":now, "data": np.random.randint(0,2)/4.0})

    

    def store_employee_to_firebase(self):
        # Use a service account
        cred = credentials.Certificate('ieor185-274323-e16b83ee9351.json')
        firebase_admin.initialize_app(cred)

        db = firestore.client()

        doc_ref = db.collection(u'employees').document(u'{}'.format(self.id))
        d = vars(self)
        del d['weather_constant']
        del d['traffic_constant']
        del d['chat_tone_constant']
        doc_ref.set(d)

    def run(self):
        self.get_daily_stats()
        self.run_sensors()
        self.get_api_stats()
        self.store_employee_to_firebase()


e = Employee(name="Sudarshan", 
        id=1,
        age=21, 
        gender="male", 
        bodyfat="22", 
        height="168", 
        weight="190", 
        zipcode="94704", 
        department="Engineering", 
        team="Infrastructure", 
        stock_symbol="GOOG"
    )

e.run()








    
        

        
        
        

