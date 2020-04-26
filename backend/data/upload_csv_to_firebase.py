import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

def delete_collection(coll_ref, batch_size):
    db = firestore.client()
    coll_ref = db.collection(u'{}'.format(coll_ref))
    docs = coll_ref.get()

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()


cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)




db = firestore.client()

delete_collection("state_prediction", 50)
delete_collection("health_prediction", 50)

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



