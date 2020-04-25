
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import pickle
from google.cloud import storage
from io import StringIO
import os


# In[2]:

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score
from sklearn.semi_supervised import LabelPropagation, LabelSpreading


# In[3]:

def build_predictor_model(X, y):
    logistic_classifier = LogisticRegressionCV()
    logistic_classifier.fit(X, y)
    print("Classifier Accuracy:", logistic_classifier.score(X, y))
    return logistic_classifier 


# In[4]:

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


# In[5]:

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

def create_models(df):
    X, Y = sanitize_input_data(df)    
    # Dataset - Depression
    X_depression, y_depression = X.copy(), Y.iloc[:,0]
    depression_model = build_predictor_model(X_depression, y_depression)
    save_predictor_model(depression_model, "sore throat")
    
    # Dataset - SAD
    X_sad, y_sad = X.copy(), Y.iloc[:,1]
    sad_model = build_predictor_model(X_sad, y_sad)
    save_predictor_model(depression_model, "fever")
    
    # Dataset - Lombago
    X_lombago, y_lombago = X.copy(), Y.iloc[:,2]
    lombago_model = build_predictor_model(X_lombago, y_lombago)
    save_predictor_model(depression_model, "cough")
    
    # Dataset - Carpal Tunnel
    X_ct, y_ct = X.copy(), Y.iloc[:,3]
    ct_model = build_predictor_model(X_ct, y_ct)
    save_predictor_model(depression_model, "allergy")


# In[8]:

def load_input():
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


# In[10]:

df = load_input()
create_models(df)


# In[ ]:



