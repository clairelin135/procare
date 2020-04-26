
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
from io import BytesIO
import ast


# In[2]:

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('key.json')  
firebase_admin.initialize_app(cred)


# In[3]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score


# In[4]:

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


# In[5]:

def load_predictor_model(name):
    bucket_name = "ieor185-274323.appspot.com"
    blob_name = name

    storage_client = storage.Client.from_service_account_json('key.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    bytes_data = blob.download_as_string()
    
    data = BytesIO(bytes_data)
    
    loaded_model = pickle.Unpickler(data).load()
    
    return loaded_model


# In[6]:

def sanitize_input_data(df):
    X = df.iloc[:,1:-4]
    Y = df.iloc[:,-4:]
    
    # Data Sanitization
    X['has_roommates'] = X['has_roommates'].apply(lambda x: 1 if x.lower() == 'y' else 0)
    X['percent_work_done_in_teams'] = X['percent_work_done_in_teams'].apply(lambda x: float(str(x)[:-1])/100)
    X['public_transit_commute'] = X['public_transit_commute'].apply(lambda x: 1 if x.lower() == 'y' else 0)
    X['lunch_cafeteria_or_other'] = X['lunch_cafeteria_or_other'].apply(lambda x: 1 if x.lower() == 'c' else 0)
    X['gender'] = X['gender'].apply(lambda x: 1 if x.lower() == 'male' else 0)

    X = one_hot_encoding(X, "location")
    X = one_hot_encoding(X, "season")
    
    
    return X, Y


# In[7]:

def load_input_firebase():
    keys_all = ['ID', 'age', 'gender', 'weight', 'num_task_pending',
       'average_task_completion_delay', 'avg_sleep', 'calories_eaten',
       'water_drank', 'lunch_cafeteria_or_other', 'percent_work_done_in_teams',
       'public_transit_commute', 'entry time', 'exit time', 'hours', 'height',
       'num_breaks', 'season', 'location', 'has_roommates', 'num_laundry',
        "sore throat","fever","cough","allergy symptoms"]
    
    db = firestore.client()
    
    docs = db.collection(u'health_prediction').get()
    rows = []
    
    for doc in docs:
        rows.append(doc.to_dict())
        
    return pd.DataFrame(data=rows, columns=keys_all).dropna()


# In[8]:

def get_prediction(inp, name):
    keys = ['ID', 'age', 'gender', 'weight', 'num_task_pending',
       'average_task_completion_delay', 'avg_sleep', 'calories_eaten',
       'water_drank', 'lunch_cafeteria_or_other', 'percent_work_done_in_teams',
       'public_transit_commute', 'entry time', 'exit time', 'hours', 'height',
       'num_breaks', 'season', 'location', 'has_roommates', 'num_laundry']
    
    
    final = {}
    
    for key in keys:
        if key in inp:
            final[key] = inp[key]
        else:
            return -1
    
    df = load_input_firebase()
    df = df.append(final, ignore_index=True)
    X, Y = sanitize_input_data(df)
        
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


# In[ ]:




# In[ ]:



