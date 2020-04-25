
# coding: utf-8

# In[70]:

import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
from io import BytesIO
import ast


# In[71]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score


# In[72]:

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
    


# In[73]:

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


# In[74]:

def sanitize_input_data(df):
    X = df.iloc[:,1:-4]
    
    # Data Sanitization
    X['stock'] = X['stock'].apply(lambda x: float(str(x)[:-1])/100)  
    X['weather'] = X['weather'].apply(lambda x: x.lower())
    X = one_hot_encoding(X, 'gender')
    X = one_hot_encoding(X, 'weather')
    X = one_hot_encoding(X, 'average_chat_tone')
    X['traffic condition'] = X['traffic condition'].apply(traffic_condition_processing)
    X['chat-words-depression'], X['chat-words-sad'], X['chat-words-lumbago'] = X['chat-words'].apply(lambda x: chat_words_processing(x, "depression")), X['chat-words'].apply(lambda x: chat_words_processing(x, "sad")), X['chat-words'].apply(lambda x: chat_words_processing(x, "lumbago"))
    X = X.drop(columns=["stock_ticker", "chat-words"])
    
    return X
    


# In[75]:

def load_csv_input():
    bucket_name = "ieor185-274323.appspot.com"
    blob_name = "state_prediction.csv"

    storage_client = storage.Client.from_service_account_json('key.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    bytes_data = blob.download_as_string()
    
    s = str(bytes_data,'utf-8')
    data = StringIO(s) 
    
    df = pd.read_csv(data)
    return df


# In[76]:

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
            final[key] = inp[key]
        else:
            return -1
    
    df = load_csv_input()
    df = df.append(final, ignore_index=True)
    X = sanitize_input_data(df)
    
    
    model = load_predictor_model(name)
    
    
    return model.predict_proba(X)[-1][1]
        


# In[77]:

inp = {'ID':0, 
       'age':21, 
       'gender':"male", 
       'body_fat_percentage':12, 
       'height':169, 
       'weight':200,
       'num_breaks':5, 
       'num_task_pending':234, 
       'average_task_completion_delay':1000,
       'calories_eaten':500, 
       'morning push percentage':0.2,
       'afternoon push percentage':0.6, 
       'evening push percentage':0.2,
       'git_avg_push_time_difference':10, 
       'average_chat_tone':'Angry',
       'ergonomic_risk_rating':5, 
       'number of times standing':1,
       'minutes_worked_out':0, 
       'average_heart_rate':180, 
       'traffic condition':'Red',
       'chat-words':"bad", 
       'location':"77494", 
       'workplace temperature':"23", 
       'weather':"rainy",
       'entry time':3, 
       'exit time':23, 
       'stock_ticker':"GOOG", 
       'stock':"-35%", 
       'hours':40}

get_prediction(inp, "depression")
