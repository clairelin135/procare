import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd


cred = credentials.Certificate('ieor185-274323-e16b83ee9351.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

d = pd.read_csv("data/state_prediction.csv").to_dict("index")


for r in d:
    doc_ref = db.collection(u'state_prediction').document(u'{}'.format(r))
    doc_ref.set(d[r])

doc_ref = db.collection(u'state_prediction').document(u'metadata')
doc_ref.set({"row_count": len(d)})


