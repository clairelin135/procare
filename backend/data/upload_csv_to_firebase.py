import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd


cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

d = pd.read_csv("state_prediction.csv").to_dict("index")


for r in d:
    doc_ref = db.collection(u'state_prediction').document(u'{}'.format(r))
    doc_ref.set(d[r])

doc_ref = db.collection(u'state_prediction').document(u'metadata')
doc_ref.set({"row_count": len(d)})


d = pd.read_csv("health_prediction.csv").to_dict("index")


for r in d:
    doc_ref = db.collection(u'health_prediction').document(u'{}'.format(r))
    doc_ref.set(d[r])

doc_ref = db.collection(u'health_prediction').document(u'metadata')
doc_ref.set({"row_count": len(d)})



