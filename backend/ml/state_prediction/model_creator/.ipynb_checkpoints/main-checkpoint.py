
# coding: utf-8

# In[30]:

import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
import os


# In[31]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score
from sklearn.semi_supervised import LabelPropagation, LabelSpreading


# In[32]:

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
    


# In[33]:

def build_predictor_model(X, y):
    logistic_classifier = LogisticRegressionCV()
    logistic_classifier.fit(X, y)
    print("Classifier Accuracy:", logistic_classifier.score(X, y))
    return logistic_classifier 


# In[34]:

def save_predictor_model(model, name):
    filename = '{}.sav'.format(name)
    pickle.dump(model, open(filename, 'wb'))
    
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
    
    os.remove(filename)


# In[35]:

def sanitize_input_data(df):
    X = df.iloc[:,1:-4]
    Y = df.iloc[:,-4:]
    
    # Data Sanitization
    X['stock'] = X['stock'].apply(lambda x: float(str(x)[:-1])/100)  
    X['weather'] = X['weather'].apply(lambda x: x.lower())
    X = one_hot_encoding(X, 'gender')
    X = one_hot_encoding(X, 'weather')
    X = one_hot_encoding(X, 'average_chat_tone')
    X['traffic condition'] = X['traffic condition'].apply(traffic_condition_processing)
    X['chat-words-depression'], X['chat-words-sad'], X['chat-words-lumbago'] = X['chat-words'].apply(lambda x: chat_words_processing(x, "depression")), X['chat-words'].apply(lambda x: chat_words_processing(x, "sad")), X['chat-words'].apply(lambda x: chat_words_processing(x, "lumbago"))
    X = X.drop(columns=["stock_ticker", "chat-words"])
    
    return X, Y
    


# In[36]:

def create_models(df):
    X, Y = sanitize_input_data(df)
    
    # Dataset - Depression
    X_depression, y_depression = X.copy(), Y.iloc[:,0]
    depression_model = build_predictor_model(X_depression, y_depression)
    save_predictor_model(depression_model, "depression")
    
    # Dataset - SAD
    X_sad, y_sad = X.copy(), Y.iloc[:,1]
    sad_model = build_predictor_model(X_sad, y_sad)
    save_predictor_model(depression_model, "sad")
    
    # Dataset - Lombago
    X_lombago, y_lombago = X.copy(), Y.iloc[:,2]
    lombago_model = build_predictor_model(X_lombago, y_lombago)
    save_predictor_model(depression_model, "lombago")
    
    # Dataset - Carpal Tunnel
    X_ct, y_ct = X.copy(), Y.iloc[:,3]
    ct_model = build_predictor_model(X_ct, y_ct)
    save_predictor_model(depression_model, "ct")


# In[37]:

def load_input():
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


# In[38]:

df = load_input()
create_models(df)


# In[ ]:




# In[ ]:



