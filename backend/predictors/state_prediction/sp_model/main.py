
# coding: utf-8

# In[15]:

import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
from io import BytesIO
import ast


# In[16]:

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('key.json')  
firebase_admin.initialize_app(cred)


# In[17]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score


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
    bytes_data = blob.download_as_string()
    
    data = BytesIO(bytes_data)
    
    loaded_model = pickle.Unpickler(data).load()
    
    return loaded_model


# In[20]:

def sanitize_input_data(df):
    X = df.iloc[:,1:-4]
     
    X['weather'] = X['weather'].apply(lambda x: x.lower())
    X = one_hot_encoding(X, 'gender')
    X = one_hot_encoding(X, 'weather')
    X = one_hot_encoding(X, 'average_chat_tone')
    X['traffic condition'] = X['traffic condition'].apply(traffic_condition_processing)
    X['chat-words-depression'], X['chat-words-sad'], X['chat-words-lumbago'] = X['chat-words'].apply(lambda x: chat_words_processing(x, "depression")), X['chat-words'].apply(lambda x: chat_words_processing(x, "sad")), X['chat-words'].apply(lambda x: chat_words_processing(x, "lumbago"))
    X = X.drop(columns=["stock_ticker", "chat-words"])
    
    return X
    


# In[21]:

def load_input_firebase():
    keys_all = ['ID', 'age', 'gender', 'body_fat_percentage', 'height', 'weight',
       'num_breaks', 'num_task_pending', 'average_task_completion_delay',
       'calories_eaten', 'morning push percentage',
       'afternoon push percentage', 'evening push percentage',
       'git_avg_push_time_difference', 'average_chat_tone',
       'ergonomic_risk_rating', 'number of times standing',
       'minutes_worked_out', 'average_heart_rate', 'traffic condition',
       'chat-words', 'location', 'workplace temperature', 'weather',
       'entry time', 'exit time', 'stock_ticker', 'stock', 'hours',
        'DEPRESSED?', 'S.A.D.?', 'LOMBAGO', 'CARPAL TUNNEL']
    
    db = firestore.client()
    
    docs = db.collection(u'state_prediction').get()
    rows = []
    
    for doc in docs:
        rows.append(doc.to_dict())
        
    return pd.DataFrame(data=rows, columns=keys_all).dropna()


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
            final[key] = inp[key]
        else:
            return -1
    
    df = load_input_firebase()
    df = df.append(final, ignore_index=True)
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


# In[ ]:




# In[ ]:



