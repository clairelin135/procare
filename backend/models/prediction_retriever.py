def get_employee_data(user_id, db):
        doc_ref = db.collection(u'employees').document(u'{}'.format(user_id))
        return doc_ref.get().to_dict()

# State Type options: depression, sad, ct, lombago
def get_state_prediction(user_id, state_type):
    import requests, os, base64
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    cred = credentials.Certificate('key.json')  
    try:
        firebase_admin.initialize_app(cred)
    except:
        print("Already authenticated!")
    db = firestore.client()

    employee_data = get_employee_data(user_id, db)

    predictor_data = {
        'ID' : employee_data["id"],
        'age' : employee_data["age"],
        'gender' : employee_data["gender"],
        'body_fat_percentage' : employee_data["bodyfat"],
        'height' : employee_data["height"],
        'weight' : employee_data["weight"],
        'num_breaks' : 0, #employee_data[""], #TODO: Calculate
        'num_task_pending' : 0, #employee_data[""], #TODO: Calculate
        'average_task_completion_delay' : employee_data["avg_task_delay"][-1]["data"],
        'calories_eaten' : 0, #employee_data[""], #TODO: Calculate
        'morning push percentage' : employee_data["git_push_dist_morning"][-1]["data"],
        'afternoon push percentage' : employee_data["git_push_dist_afternoon"][-1]["data"],
        'evening push percentage' : employee_data["git_push_dist_evening"][-1]["data"],
        'git_avg_push_time_difference' : 0, #employee_data[""], #TODO Calculate
        'average_chat_tone' : employee_data["chat_tone"][-1]["data"],
        'ergonomic_risk_rating' :  0, #employee_data["ergonomic_risk_rating"], #TODO: Calculate timewise mean
        'number of times standing' :  0, #employee_data["stand_triggers"], #TODO: Calculate daily count
        'minutes_worked_out' : employee_data["mins_workedout"][-1] if employee_data["mins_workedout"] else 0,
        'average_heart_rate' : employee_data["heart_rate"][-1]["data"], 
        'traffic condition' : employee_data["traffic"][-1]["data"], 
        'chat-words' : "", 
        'location' : employee_data["zipcode"],
        'workplace temperature' : employee_data["temperature"][-1]["data"],
        'weather' : employee_data["weather"][-1]["data"],
        'entry time' : employee_data["entrance_time"][-1]["data"],
        'exit time' : employee_data["exit_time"][-1]["data"],
        'stock_ticker' : employee_data["stock_symbol"],
        'stock' : employee_data["stock_ytd"][-1]["data"],
        'hours' : employee_data["exit_time"][-1]["data"] - employee_data["entrance_time"][-1]["data"],   
    }

    url = "https://us-central1-ieor185-274323.cloudfunctions.net/state_prediction"
    params = {
        'inp': predictor_data,
        'name': state_type
    }


    encoded_dict = str(params).encode('utf-8')

    base64_dict = base64.b64encode(encoded_dict)

    r = requests.get(url, {'message':base64_dict})
    return eval(r.content)


# State Type options: cough, fever, sore throat, allergy
def get_health_prediction(user_id, state_type):
    import requests, os, base64
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    cred = credentials.Certificate('key.json')  
    try:
        firebase_admin.initialize_app(cred)
    except:
        print("Already authenticated!")
    db = firestore.client()

    employee_data = get_employee_data(user_id, db)

    predictor_data = {
        'ID':1, 
        'age':21, 
        'gender':"male", 
        'weight':190, 
        'num_task_pending':0,
        'average_task_completion_delay':5, 
        'avg_sleep':8, 
        'calories_eaten':2000,
        'water_drank':10, 
        'lunch_cafeteria_or_other':'c', 
        'percent_work_done_in_teams':"10%",
        'public_transit_commute':"n", 
        'entry time':9, 
        'exit time':6, 
        'hours':8, 
        'height':168,
        'num_breaks':10, 
        'season':"spring", 
        'location':"SF", 
        'has_roommates':"n", 
        'num_laundry':"0",
    }

    url = "https://us-central1-ieor185-274323.cloudfunctions.net/health_prediction"
    params = {
        'inp': predictor_data,
        'name': state_type
    }


    encoded_dict = str(params).encode('utf-8')

    base64_dict = base64.b64encode(encoded_dict)

    r = requests.get(url, {'message':base64_dict})
    return eval(r.content)
