from joblib import dump, load
import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
from io import BytesIO
import ast

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression



# In[18]:

def one_hot_encoding(data, column):
    if column not in data.columns:
        return data
    
    vec_enc = DictVectorizer()
    vec_enc.fit(data[[column]].to_dict(orient='records'))
    fireplace_qu_data = vec_enc.transform(data[[column]].to_dict(orient='records')).toarray()
    fireplace_qu_cats = vec_enc.get_feature_names()
    fireplace_qu = pd.DataFrame(fireplace_qu_data, columns=fireplace_qu_cats)
    data = pd.concat([data, fireplace_qu], axis=1)
    
    data = data.drop(columns=[fireplace_qu_cats[0], column])
    return data

def chat_words_processing(words, disease):
    buzz_words = {
        "depression":["tired", "overlooked", "depressed", "bogged down", "disheartened", "stressed", "bipolar", "drained", "fatigued"],
        "sad": ["tired", "sad", "fatigued"],
        "lumbago": ["sore", "uncomfortable", "in pain", "stiff", "irritated"],
    }
    
    words = words.split(",")
    
    score = 0
    compare_list = buzz_words[disease]
    
    for word in words:
        if word in compare_list:
            score += 1
    
    return score
    
    

def traffic_condition_processing(tc):
    if tc.lower() == 'red':
        return 2
    elif tc.lower() == 'yellow':
        return 1
    else:
        return 0
    


# In[19]:

def load_predictor_model(name):
    bucket_name = "ieor185-274323.appspot.com"
    blob_name = name

    storage_client = storage.Client.from_service_account_json('key.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    filename = '{}.sav'.format(name)
    f = open(filename, 'wb')
    blob.download_to_filename(filename)
    loaded_model = load(filename)
    
    return loaded_model


# In[20]:

def sanitize_input_data(df):  
    X = df.iloc[:,1:]
    X['weather'] = X['weather'].apply(lambda x: x.lower())
    X['gender'] = X['gender'].apply(lambda x: 1 if x.lower() =='male' else 0)
    # X = one_hot_encoding(X, 'weather')
    # X = one_hot_encoding(X, 'average_chat_tone')
    X['traffic condition'] = X['traffic condition'].apply(traffic_condition_processing)
    X['chat-words-depression'], X['chat-words-sad'], X['chat-words-lumbago'] = X['chat-words'].apply(lambda x: chat_words_processing(x, "depression")), X['chat-words'].apply(lambda x: chat_words_processing(x, "sad")), X['chat-words'].apply(lambda x: chat_words_processing(x, "lumbago"))
    X = X.drop(columns=["stock_ticker", "chat-words", "weather", "average_chat_tone"])
    return X
    


# In[21]:

# def load_input_firebase():
#     keys_all = ['ID', 'age', 'gender', 'body_fat_percentage', 'height', 'weight',
#        'num_breaks', 'num_task_pending', 'average_task_completion_delay',
#        'calories_eaten', 'morning push percentage',
#        'afternoon push percentage', 'evening push percentage',
#        'git_avg_push_time_difference', 'average_chat_tone',
#        'ergonomic_risk_rating', 'number of times standing',
#        'minutes_worked_out', 'average_heart_rate', 'traffic condition',
#        'chat-words', 'location', 'workplace temperature', 'weather',
#        'entry time', 'exit time', 'stock_ticker', 'stock', 'hours',
#         'DEPRESSED?', 'S.A.D.?', 'LOMBAGO', 'CARPAL TUNNEL']
    
#     db = firestore.client()
    
#     docs = db.collection(u'state_prediction').get()
#     rows = []
    
#     for doc in docs:
#         rows.append(doc.to_dict())
        
#     return pd.DataFrame(data=rows, columns=keys_all).dropna()


# In[22]:

def get_prediction(inp, name):
    keys = ['ID', 'age', 'gender', 'body_fat_percentage', 'height', 'weight',
       'num_breaks', 'num_task_pending', 'average_task_completion_delay',
       'calories_eaten', 'morning push percentage',
       'afternoon push percentage', 'evening push percentage',
       'git_avg_push_time_difference', 'average_chat_tone',
       'ergonomic_risk_rating', 'number of times standing',
       'minutes_worked_out', 'average_heart_rate', 'traffic condition',
       'chat-words', 'location', 'workplace temperature', 'weather',
       'entry time', 'exit time', 'stock_ticker', 'stock', 'hours']
    
    final = {}
    
    for key in keys:
        if key in inp:
            final[key] = [inp[key]]
        else:
            return -1
    
    df = pd.DataFrame.from_dict(final)
    X = sanitize_input_data(df)
    
    model = load_predictor_model(name)
    
    
    return str(model.predict_proba(X)[-1][1])
        


def main(request):
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        import base64
        x = request.args.get('message')
        params = eval(base64.b64decode(x))
        return get_prediction(params['inp'], params['name'])

    return f'Error In Parameter'


def get_employee_data(user_id, db):
    doc_ref = db.collection(u'employees').document(u'{}'.format(user_id))
    return doc_ref.get().to_dict()

# State Type options: depression, sad, ct, lombago
def get_state_prediction(user_id, state_type):
    import requests, os, base64
    import numpy as np
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    cred = credentials.Certificate('key.json')  
    try:
        firebase_admin.initialize_app(cred)
    except:
        x = 2

    db = firestore.client()

    employee_data = get_employee_data(user_id, db)

    predictor_data = {
        'ID' : employee_data["id"],
        'age' : employee_data["age"],
        'gender' : employee_data["gender"],
        'body_fat_percentage' : employee_data["bodyfat"],
        'height' : employee_data["height"],
        'weight' : employee_data["weight"],
        'num_breaks' : np.random.randint(0,25), #employee_data[""], #TODO: Calculate
        'num_task_pending' : employee_data["num_task_pendings"][-1]["data"],
        'average_task_completion_delay' : employee_data["avg_task_delay"][-1]["data"],
        'calories_eaten' : employee_data["calories_eaten"][-1]["data"],
        'morning push percentage' : employee_data["git_push_dist_morning"][-1]["data"],
        'afternoon push percentage' : employee_data["git_push_dist_afternoon"][-1]["data"],
        'evening push percentage' : employee_data["git_push_dist_evening"][-1]["data"],
        'git_avg_push_time_difference' : employee_data["git_push_time_difference"][-1]["data"], #TODO Calculate
        'average_chat_tone' : employee_data["chat_tone"][-1]["data"],
        'ergonomic_risk_rating' :  np.mean(employee_data["ergonomic_risk_rating"][-1]["data"]), #employee_data["ergonomic_risk_rating"], #TODO: Calculate timewise mean
        'number of times standing' :  np.random.randint(0,10), #employee_data["stand_triggers"], #TODO: Calculate daily count
        'minutes_worked_out' : employee_data["mins_workedout"][-1]["data"] if employee_data["mins_workedout"] else 0,
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

    return get_prediction(predictor_data, state_type)

print("Out:" , get_state_prediction(102, "ct"))