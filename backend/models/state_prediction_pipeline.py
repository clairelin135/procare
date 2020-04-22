import numpy as np
import datetime
import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def get_employee_data(user_id, db):
    doc_ref = db.collection(u'employees').document(u'{}'.format(user_id))
    return doc_ref.get().to_dict()

def get_state_prediction_meta(db):
    doc_ref = db.collection(u'state_prediction').document(u'metadata')
    return doc_ref.get().to_dict()["row_count"]

def set_new_datastream(db, d, r):
    doc_ref = db.collection(u'state_prediction').document(u'{}'.format(r))
    doc_ref.set(d)

def set_new_rowcount(db, r):
    doc_ref = db.collection(u'state_prediction').document(u'metadata')
    doc_ref.set({"row_count": r+1})


def run(user_id):
    cred = credentials.Certificate('ieor185-274323-e16b83ee9351.json')  
    firebase_admin.initialize_app(cred)
    db = firestore.client()


    employee_data = get_employee_data(user_id, db)


    predictor_data = {
        'ID' : employee_data["id"],
        'age' : employee_data["age"],
        'gender' : employee_data["gender"],
        'body_fat_percentage' : employee_data["bodyfat"],
        'height' : employee_data["height"],
        'weight' : employee_data["weight"],
       'num_breaks' : None, #employee_data[""], #TODO: Calculate
       'num_task_pending' : None, #employee_data[""], #TODO: Calculate
       'average_task_completion_delay' : employee_data["avg_task_delay"][-1]["data"],
       'calories_eaten' : None, #employee_data[""], #TODO: Calculate
       'morning push percentage' : employee_data["git_push_dist_morning"][-1]["data"],
       'afternoon push percentage' : employee_data["git_push_dist_afternoon"][-1]["data"],
       'evening push percentage' : employee_data["git_push_dist_evening"][-1]["data"],
       'git_avg_push_time_difference' : None, #employee_data[""], #TODO Calculate
       'average_chat_tone' : employee_data["chat_tone"][-1]["data"],
       'ergonomic_risk_rating' :  None, #employee_data["ergonomic_risk_rating"], #TODO: Calculate timewise mean
       'number of times standing' :  None, #employee_data["stand_triggers"], #TODO: Calculate daily count
       'minutes_worked_out' : employee_data["mins_workedout"],
       'average_heart_rate' : employee_data["heart_rate"][-1]["data"], 
       'traffic condition' : employee_data["traffic"][-1]["data"], 
       'chat-words' : [], 
       'location' : employee_data["zipcode"],
       'workplace temperature' : employee_data["temperature"][-1]["data"],
       'weather' : employee_data["weather"][-1]["data"],
       'entry time' : employee_data["entrance_time"][-1]["data"],
       'exit time' : employee_data["exit_time"][-1]["data"],
       'stock_ticker' : employee_data["stock_symbol"],
       'stock' : employee_data["stock_ytd"][-1]["data"],
       'hours' : employee_data["exit_time"][-1]["data"] - employee_data["entrance_time"][-1]["data"],   
    }

    predictor_data["CARPAL TUNNEL"] = -1 # Call HTTP Endpoint
    predictor_data["DEPRESSED?"] = -1 # Call HTTP Endpoint
    predictor_data["LOMBAGO"] = -1 # Call HTTP Endpoint
    predictor_data["S.A.D.?"] = -1 # Call HTTP Endpoint
    
    r = get_state_prediction_meta(db)
    set_new_datastream(db, predictor_data, r)
    set_new_rowcount(db, r)

run(1)