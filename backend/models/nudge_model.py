import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class NudgePackage:
    def __init__(self, to_user_id, nudge_time, nudge_question):
        self.to_user_id = to_user_id
        self.nudge_time = nudge_time
        self.nudge_question = nudge_question
        self.nudge_response = "Response Goes Here"
        self.responded = False
        self.sent = False

    def send(self):
        cred = credentials.Certificate('ieor185-274323-e16b83ee9351.json')
        firebase_admin.initialize_app(cred)

        db = firestore.client()

        doc_ref = db.collection(u'nudges-{}'.format(self.to_user_id)).document(u'{}'.format(self.nudge_time))
        doc_ref.set(vars(self))

class NudgeManager:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def get_data_from_firestore(self):
        cred = credentials.Certificate('ieor185-274323-e16b83ee9351.json')
        firebase_admin.initialize_app(cred)

        db = firestore.client()

        doc_ref = db.collection(u'employees').document(u'{}'.format(self.user_id))
        return doc_ref.get().to_dict()

    def run(self):
        now = datetime.datetime.now()

        # Nudge Call 1
        nudge1 = NudgePackage(to_user_id=1, nudge_time=now, nudge_question="This is a question")
        nudge1.send()
        # Nudge Call 2

        # Nudge Call 3
        

nudge = NudgeManager(1)
nudge.run()

