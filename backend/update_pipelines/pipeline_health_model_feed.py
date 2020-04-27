import numpy as np
import datetime
import random

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate('key.json')  
firebase_admin.initialize_app(cred)

def get_employee_data(user_id, db):
    doc_ref = db.collection(u'employees').document(u'{}'.format(user_id))
    return doc_ref.get().to_dict()

def get_health_prediction_meta(db):
    doc_ref = db.collection(u'health_prediction').document(u'metadata')
    return doc_ref.get().to_dict()["row_count"]

def set_new_datastream(db, d, r):
    doc_ref = db.collection(u'health_prediction').document(u'{}'.format(r))
    doc_ref.set(d)

def set_new_rowcount(db, r):
    doc_ref = db.collection(u'health_prediction').document(u'metadata')
    doc_ref.set({"row_count": r+1})


def get_health_prediction(db, user_id, state_type, predictor_data):
    import requests, os, base64

    employee_data = get_employee_data(user_id, db)

    url = "https://us-central1-ieor185-274323.cloudfunctions.net/health_prediction"
    params = {
        'inp': predictor_data,
        'name': state_type
    }

    import base64

    encoded_dict = str(params).encode('utf-8')

    base64_dict = base64.b64encode(encoded_dict)

    r = requests.get(url, {'message':base64_dict})
    return eval(r.content)


def get_user_data_for_health_prediction(db, user_id):
    employee_data = get_employee_data(user_id, db)

    predictor_data = {
        'ID' : employee_data["id"],
        'age' : employee_data["age"],
        'gender' : employee_data["gender"],
        'weight' : employee_data["weight"],
        'num_task_pending':employee_data["num_task_pendings"][-1]["data"],
        'average_task_completion_delay':employee_data["avg_task_delay"][-1]["data"], 
        'avg_sleep':employee_data["sleep"][-1]["data"], 
        'calories_eaten':employee_data["calories_eaten"][-1]["data"],
        'water_drank':employee_data["water_consumed"][-1]["data"], 
        'lunch_cafeteria_or_other':employee_data["lunch_cafeteria_or_other"][-1]["data"], 
        'percent_work_done_in_teams':employee_data["percent_work_done_in_teams"][-1]["data"],
        'public_transit_commute':employee_data["public_transit_commute"][-1]["data"], 
        'entry time':employee_data["entrance_time"][-1]["data"], 
        'exit time':employee_data["exit_time"][-1]["data"], 
        'hours':employee_data["exit_time"][-1]["data"] - employee_data["entrance_time"][-1]["data"], 
        'height':employee_data["height"],
        'num_breaks':np.random.randint(0,25), 
        'season':"spring", 
        'location':"SF", 
        'has_roommates':employee_data["roommates"], 
        'num_laundry':employee_data["num_laundry"][-1]["data"],
    }

    return predictor_data

def run_health_pipeline(user_id):
    db = firestore.client()

    df = get_user_data_for_health_prediction(db, user_id)
    predictor_data = get_user_data_for_health_prediction(db, user_id)
    predictor_data["cough"] = get_health_prediction(db, user_id, "cough", df) # Call HTTP Endpoint
    predictor_data["fever"] = get_health_prediction(db, user_id, "fever", df) # Call HTTP Endpoint
    predictor_data["sore throat"] = get_health_prediction(db, user_id, "sore throat", df) # Call HTTP Endpoint
    predictor_data["allergy symptoms"] = get_health_prediction(db, user_id, "allergy", df) # Call HTTP Endpoint
    
    r = get_health_prediction_meta(db)
    set_new_datastream(db, predictor_data, r)
    set_new_rowcount(db, r)

def main(request):
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        import base64
        user_id = request.args.get('message')
        return run_health_pipeline(user_id)

    return f'Error In Parameter'

for i in range(101, 111):
    run_health_pipeline(i)