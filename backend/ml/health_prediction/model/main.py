
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

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score


# In[3]:

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


# In[4]:

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


# In[5]:

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


# In[6]:

def load_csv_input():
    bucket_name = "ieor185-274323.appspot.com"
    blob_name = "health_prediction.csv"

    storage_client = storage.Client.from_service_account_json('key.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    bytes_data = blob.download_as_string()
    
    s = str(bytes_data,'utf-8')
    data = StringIO(s) 
    
    df = pd.read_csv(data)
    return df


# In[12]:

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
    
    df = load_csv_input()
    df = df.append(final, ignore_index=True)
    X, Y = sanitize_input_data(df)
    
    
    model = load_predictor_model(name)
        
    return str(model.predict_proba(X)[-1][1])
        


# In[14]:

inp = {
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
    'percent_work_done_in_teams':"100%",
    'public_transit_commute':"y", 
    'entry time':9, 
    'exit time':6, 
    'hours':8, 
    'height':168,
    'num_breaks':10, 
    'season':"spring", 
    'location':"SF", 
    'has_roommates':"y", 
    'num_laundry':"0",
}

get_prediction(inp, "allergy")


# In[ ]:




# In[ ]:



