import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from prediction_retriever import get_state_prediction, get_health_prediction
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

class NudgePackage:
    def __init__(self, to_user_id, nudge_time, nudge_question):
        self.to_user_id = to_user_id
        self.nudge_time = nudge_time
        self.nudge_question = nudge_question
        self.nudge_response = "Response Goes Here"
        self.response = None
        self.displayed = False

    def send(self):
        db = firestore.client()

        doc_ref = db.collection(u'nudges-{}'.format(self.to_user_id)).document(u'{}'.format(self.nudge_time))
        doc_ref.set(vars(self))

class NudgeManager:
    def __init__(self):
        self.employees = {}

        # Thresholds
        self.depression_thresh = 0.40
        self.sad_thresh = 0.85
        self.lombago_thresh = 0.30
        self.ct_thresh = 0.60
        

    def run(self):
        def now():
            return datetime.datetime.now()

        db = firestore.client()
        docs = db.collection(u'employees').get()
        exployee_count = 0
        for doc in docs:
            d = doc.to_dict()
            team = d['team']
            dept = d['department']
            
            if dept not in self.employees:
                self.employees[dept] = {team:[]}
            else:
                if team not in self.employees[dept]:
                    self.employees[dept][team] = [d]
                else:
                    self.employees[dept][team].append(d)
            exployee_count += 1

        print("Employee Count:", exployee_count)

        nudges = []

        for dept in self.employees.keys():
            for team in self.employees[dept].keys():

                # State Check
                depression_check = any([get_state_prediction(x["id"], "depression") > self.depression_thresh for x in self.employees[dept][team]])
                sad_check = any([get_state_prediction(x["id"], "sad") > self.sad_thresh for x in self.employees[dept][team]])

                if depression_check or lombago_check:
                    nudges += [NudgePackage(x["id"], now(), "Have you considered some team bonding time?") for x in self.employees[dept][team]]

                lombago_check = any([get_state_prediction(x["id"], "lombago") > self.lombago_thresh for x in self.employees[dept][team]])
                if lombago_check:
                    nudges += [NudgePackage(x["id"], now(), "I think it's time for a team walk! Are you down?") for x in self.employees[dept][team]]

                ct_checks = [get_state_prediction(x["id"], "ct") > self.ct_thresh for x in self.employees[dept][team]]
                for check, x in zip(ct_checks, self.employees[dept][team]):
                    if check:
                        nudges += [NudgePackage(x["id"], now(), "Hey! I think you should take a break! Considered grabbing a quick bite?")]


                # Health Check
                for x in self.employees[dept][team]:
                    cough = get_health_prediction(x["id"], "cough")
                    fever = get_health_prediction(x["id"], "fever")
                    allergy = get_health_prediction(x["id"], "allergy")
                    sore_throat = get_health_prediction(x["id"], "sore throat")

                    if fever > 0.25:
                        nudges += [NudgePackage(x["id"], now(), "It seems that you might be under the weather. I think you should consider going home")]
                    elif sore_throat > 0.05 or cough > 0.05:
                        nudges += [NudgePackage(x["id"], now(), "It seems that you might be under the weather. I think you should consider taking a break!")]
                    elif allergy > 0.05:
                        nudges += [NudgePackage(x["id"], now(), "It seems that you might have allergies soon. Try social distancing!")]


        for nudge in nudges:
            nudge.send()
        
def delete_collection(coll_ref, batch_size):
    db = firestore.client()
    coll_ref = db.collection(u'{}'.format(coll_ref))
    docs = coll_ref.get()

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()

for i in range(101, 150):
    delete_collection("nudges-{}".format(i), 50)

NudgeManager().run()