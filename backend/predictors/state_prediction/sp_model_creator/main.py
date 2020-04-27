
# coding: utf-8

# In[1]:
from joblib import dump, load
import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
import os


# In[2]:

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('key.json')  
firebase_admin.initialize_app(cred)


# In[3]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegressionCV


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
    


# In[5]:

def build_predictor_model(X, y):
    logistic_classifier = LogisticRegressionCV()
    logistic_classifier.fit(X, y)
    print("Classifier Accuracy:", logistic_classifier.score(X, y))
    return logistic_classifier 


# In[6]:

def save_predictor_model(model, name):
    filename = 'tmp/{}.sav'.format(name)
    dump(model, open(filename, 'wb'))
    
    bucket_name = "ieor185-274323.appspot.com"
    source_file_name = filename
    destination_blob_name = name

    storage_client = storage.Client.from_service_account_json('key.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
    
    # os.remove(filename)


# In[7]:

def sanitize_input_data(df):
    X = df.iloc[:,1:-4]
    Y = df.iloc[:,-4:]
    
    X['weather'] = X['weather'].apply(lambda x: x.lower())
    X['gender'] = X['gender'].apply(lambda x: 1 if x.lower() =='male' else 0)
    # X = one_hot_encoding(X, 'weather')
    # X = one_hot_encoding(X, 'average_chat_tone')
    X['traffic condition'] = X['traffic condition'].apply(traffic_condition_processing)
    X['chat-words-depression'], X['chat-words-sad'], X['chat-words-lumbago'] = X['chat-words'].apply(lambda x: chat_words_processing(x, "depression")), X['chat-words'].apply(lambda x: chat_words_processing(x, "sad")), X['chat-words'].apply(lambda x: chat_words_processing(x, "lumbago"))
    X = X.drop(columns=["stock_ticker", "chat-words", "weather", "average_chat_tone"])
    print(X.columns)
    return X, Y
    


# In[8]:

def create_models(df):
    X, Y = sanitize_input_data(df)
    
    # Dataset - Depression
    X_depression, y_depression = X.copy(), Y.iloc[:,0]
    y_depression = y_depression.apply(lambda x: 1 if x > 0.5 else 0)
    depression_model = build_predictor_model(X_depression, y_depression)
    save_predictor_model(depression_model, "depression")
    
    # Dataset - SAD
    X_sad, y_sad = X.copy(), Y.iloc[:,1]
    y_sad = y_depression.apply(lambda x: 1 if x > 0.5 else 0)
    sad_model = build_predictor_model(X_sad, y_sad)
    save_predictor_model(depression_model, "sad")
    
    # Dataset - Lombago
    X_lombago, y_lombago = X.copy(), Y.iloc[:,2]
    y_lombago = y_depression.apply(lambda x: 1 if x > 0.5 else 0)
    lombago_model = build_predictor_model(X_lombago, y_lombago)
    save_predictor_model(depression_model, "lombago")
    
    # Dataset - Carpal Tunnel
    X_ct, y_ct = X.copy(), Y.iloc[:,3]
    y_ct = y_ct.apply(lambda x: 1 if x > 0.5 else 0)
    ct_model = build_predictor_model(X_ct, y_ct)
    save_predictor_model(depression_model, "ct")


# In[9]:

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


# In[10]:
def main(request):
    df = load_input_firebase()
    create_models(df)

main("")
