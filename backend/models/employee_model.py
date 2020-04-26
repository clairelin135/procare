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
        self.sleep = []
        self.public_transit_commute = []
        self.num_laundry = []

        # Sensor - API
        self.num_task_pendings = []
        self.avg_task_delay = []
        self.git_push_time_difference = []
        self.heart_rate = []
        self.weather = []
        self.temperature = []
        self.stock_ytd = []
        self.chat_tone = []
        
        self.lunch_cafeteria_or_other = []
        self.percent_work_done_in_teams = []
        self.season = []
        
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
        self.public_transit_constant = ["y", "n"]
        self.lunch_cafeteria_constant = ["c", "o"]
        self.roommates = ["y", "n"][np.random.randint(0, 2)]
        self.season_constant = ["fall","spring","summer", "winter"]
        
        
        

    def get_daily_stats(self):
        now = datetime.datetime.now()
        self.entrance_time.append({"time":now, "data":np.random.randint(3,11)})
        self.exit_time.append({"time":now, "data":np.random.randint(15,23)})
        self.traffic.append({"time":now, "data":self.traffic_constant[np.random.randint(0, len(self.traffic_constant))]})
        self.public_transit_commute.append({"time":now, "data":self.public_transit_constant[np.random.randint(0, len(self.public_transit_constant))]})
        self.lunch_cafeteria_or_other.append({"time":now, "data":self.lunch_cafeteria_constant[np.random.randint(0, len(self.public_transit_constant))]})
        self.season.append({"time":now, "data":self.season_constant[np.random.randint(0, len(self.season_constant))]})
        
        x = np.random.random()
        y = (1-x) * np.random.random()
        z = 1 - x - y

        self.git_push_dist_morning.append({"time":now, "data":x})
        self.git_push_dist_afternoon.append({"time":now, "data":y})
        self.git_push_dist_evening.append({"time":now, "data":z})
        self.avg_task_delay.append({"time":now, "data":np.random.randint(0, 50)})
        self.num_task_pendings.append({"time":now, "data":np.random.randint(0,100)})
        self.percent_work_done_in_teams.append({"time":now, "data":str(np.random.randint(0,100))+"%"})
        
        self.sleep.append({"time":now, "data":np.random.randint(0, 10)})
        self.calories_eaten.append({"time":now, "data":np.random.randint(0, 2500)})
        self.mins_workedout.append({"time":now, "data":np.random.randint(0, 120)})
        self.water_consumed.append({"time":now, "data":np.random.randint(0, 8)})
        self.num_laundry.append({"time":now, "data":np.random.randint(0, 10)})
        


    
    def get_api_stats(self):
        now = datetime.datetime.now()
        self.git_push_time_difference.append({"time":now, "data":np.random.randint(5, 15)}) # Supposed to get from Git livetime
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
        db = firestore.client()

        doc_ref = db.collection(u'employees').document(u'{}'.format(self.id))
        doc_ref.set(vars(self))

        firebase_admin

    def run_every_15_mins(self):
        self.run_sensors()
        self.store_employee_to_firebase()

    def run_every_day(self):
        self.get_daily_stats()
        self.run_sensors()
        self.get_api_stats()
        self.store_employee_to_firebase()


# For Data Generation
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

names = ["Selina Key",
"Jordon Clayton",
"Israel Christensen",
"Bradyn Wang",
"Jewel Gaines",
"Bryan Crane",
"Derrick Juarez",
"Zain Carter",
"Angelique Hernandez",
"America Bernard",
"Abbie Shaw",
"Jamya Stark",
"Violet Mullins",
"Lucas Marquez",
"Casey Le",
"Arjun Patel",
"Kate Stevenson",
"Lamar Luna",
"Krista Perry",
"Mya Perry",
"Ryan Chang",
"Aracely Stevenson",
"Billy Barry",
"Madelyn Flores",
"Holden Oconnell",
"Leland Davidson",
"Samuel Fitzpatrick",
"Emanuel Valenzuela",
"Janiah Melton",
"Juliana Mcneil",
"Cassie Zimmerman",
"Kolby Barr",
"Abbigail Lloyd",
"Alan Mcguire",
"Santino Mendoza",
"Hazel Dennis",
"Sienna Andrews",
"Derrick Bowen",
"Parker Clayton",
"Kobe Huffman",
"Emma Boyer",
"Ellen Raymond",
"Yasmin Summers",
"Nadia Shepherd",
"Maggie Mitchell",
"Ruben Crane",
"Aileen Monroe",
"Tommy Gibbs",
"Araceli Nelson",
"Lola Meyer"]

for user_id in range(100, 150):
    print("user id:", user_id)
    e = Employee(name=names[user_id%len(names)], 
            id=user_id,
            age=np.random.randint(18, 65), 
            gender="male", 
            bodyfat=np.random.randint(5,25), 
            height=np.random.randint(140,180), 
            weight=np.random.randint(100,200), 
            zipcode=np.random.randint(10000,99999), 
            department=["Cloud", "Ads", "Search", "Products", "Corporate"][np.random.randint(0,5)], 
            team=["Engineering", "Marketing", "Operations"][np.random.randint(0, 3)], 
            stock_symbol="GOOG"
        )

    for i in range(96):
        e.run_every_15_mins()

        if i % 96 == 0:
            e.run_every_day()

# # -------------------------

# e = Employee(name="Sudarshan's Clone 2", 
#         id=2,
#         age=21, 
#         gender="male", 
#         bodyfat="22", 
#         height="168", 
#         weight="190", 
#         zipcode="94704", 
#         department="Engineering", 
#         team="Infrastructure", 
#         stock_symbol="GOOG"
#     )

# for i in range(96 * 2):
#     e.run_every_15_mins()

#     if i % 96 == 0:
#         print(i)
#         e.run_every_day()

# # -------------------------

# e = Employee(name="Sudarshan's Clone 3", 
#         id=3,
#         age=21, 
#         gender="male", 
#         bodyfat="22", 
#         height="168", 
#         weight="190", 
#         zipcode="94704", 
#         department="Engineering", 
#         team="Infrastructure", 
#         stock_symbol="GOOG"
#     )

# for i in range(96 * 5):
#     e.run_every_15_mins()

#     if i % 96 == 0:
#         print(i)
#         e.run_every_day()









    
        

        
        
        
