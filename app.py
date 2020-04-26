# app.py
# Required Imports
import os
import json
import pyrebase
from flask import Flask, request, jsonify, render_template, url_for, redirect
from firebase_admin import credentials, firestore, initialize_app
from bokeh.plotting import figure
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from wtforms import Form, BooleanField
import requests

# config = {
#     "apiKey": "AIzaSyBdvsfqF_yfU5uvbu6tJxqAuU_jZQw86DQ",
#     "authDomain": "ieor185-274323.firebaseapp.com",
#     "databaseURL": "https://ieor185-274323.firebaseio.com",
#     "projectId": "ieor185-274323",
#     "storageBucket": "ieor185-274323.appspot.com",
#     "messagingSenderId": "746504989082",
#     "appId": "1:746504989082:web:43f738d1eaa972e1913223",
#     "measurementId": "G-1SCRZGN73Q"
# }

# Initialize Flask App
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()

# Initialize Firestore DB Constants
EMPLOYER_COLLECTION = "employers"
EMPLOYEE_COLLECTION = "employees"
NUDGE_COLLECTION = "nudges"

EMPLOYER_ROUTE = "/employer/"
EMPLOYEE_ROUTE = "/employee/"      

@app.route('/')
def index():
    employees = []
    employers = []

    employee_docs = db.collection(EMPLOYEE_COLLECTION).stream()
    for doc in employee_docs:
        json_doc = doc.to_dict()
        employee = {
            "name": json_doc["name"],
            "route": EMPLOYEE_ROUTE + str(doc.id)
        }
        employees.append(employee)

    # employer_docs = db.collection(EMPLOYER_COLLECTION).stream()
    # for doc in employer_docs:
    #     json_doc = doc.to_dict()
    #     employer = {
    #         "name": json_doc["name"]
    #         "id": doc.id
    #     }
    #     employers.append(employer)
    
    return render_template("index.html", employees=employees, employers=employers)


@app.route(EMPLOYEE_ROUTE + '<id>', methods=['GET', 'POST'])
def employee(id):
    class F(Form):
        pass
    
    # Fetch nudges and add to document
    nudges = []
    point_count = 0
    nudges_ref = db.collection(NUDGE_COLLECTION + "-1").stream()
    for nudge in nudges_ref:
        nudge_id = nudge.id
        nudge = nudge.to_dict()
        nudge["id"] = nudge_id
        if nudge["responded"] == False: # Only display nudges that the user has not responded to
            nudges.append(nudge)
        elif nudge["sent"] == True: # User accepted the nudge
            point_count += 1
    for nudge in nudges:
        setattr(F, nudge["id"], BooleanField(label=nudge["nudge_question"]))
    
    if request.method == 'POST':
        form = F(request.form)
        for (key, value) in form.data.items():
            try:
                doc_ref = db.collection(NUDGE_COLLECTION + "-1").document(key)
                doc_ref.update({
                    "sent": value,
                    "responded": True
                })
                delattr(F, key)
            except Exception as e:
                return f"An Error Occured: {e}"
        setattr(F, '_unbound_fields', [])
        return redirect(request.url)

    form = F(request.form)
    doc_ref = db.collection(EMPLOYEE_COLLECTION).document(str(id))
    doc = doc_ref.get()

    if doc.exists:
        doc = doc.to_dict()

        doc["points"] = point_count
        doc["tree_height"] = str(min(500, 150 + point_count * 50)) + "px"

        doc["water_percentage"] = round(round(120/600, 2)*100)
        doc["focus_percentage"] = round(round(55/120, 2)*100)

        break_duration_len = min(32, len(doc["break_durations"]))
        x = []
        y = []
        for b in doc["break_durations"][-break_duration_len:]:
            x.append(b["time"])
            y.append(sum(b["data"]))

        p = figure(plot_width=550, plot_height=300)

        # add both a line and circles on the same plot
        p.line(x, y, line_width=2, line_color="#8CCFBB")
        p.toolbar_location = None
        p.xaxis.axis_label = "Time"
        p.xaxis.formatter = DatetimeTickFormatter(hourmin = ['%H:%M'])
        p.yaxis.axis_label = "Minutes spent walking/standing"

        script, div = components(p)

        return render_template("employee.html", data=doc, div=div, script=script, form=form)
    else:
        return f"User does not exist"

db_m = {'1': 'engineering', '2': 'product-management', '3': 'sales'}
human_m = {'1': 'Engineering', '2': 'Product', '3': 'Sales'}
@app.route(EMPLOYER_ROUTE + '<id>', methods=['GET', 'POST'])
def employer(id):
    document = db_m[id]
    
    emo_p = get_weekly_average(document, "emotional_level")
    pro_p = get_weekly_average(document, "productivity")
    phy_p = get_weekly_average(document, "physical_wellness")
    admin_name = get_admin_name(db_m[id])
    print(emo_p)
    print(pro_p)
    print(phy_p)

    
    doc = {'emotion-percentage': str(emo_p)+'%',
            'product-percentage': str(pro_p)+'%',
            'physical-percentage': str(phy_p)+'%',
            'attendance': 300,
            'late': 10,
            'absent': 5,
            'admin-name': admin_name,
            'dep-name': human_m[id]
        }

    return render_template("employer.html", data=doc)

# document: [product-management, engineering, sales]
# stat: [emotional_level, productivity, physical_wellness]
def get_weekly_average(department, stat):
    total = 0
    day = 21
    for _ in range(7):
        date = "2020-04-" + str(day)
        doc_stream = db.collection(EMPLOYER_COLLECTION).document(date).collection(department).stream()
        for doc in doc_stream:
            json_doc = doc.to_dict()
            p = json_doc[stat]
            total += p
            break
        day -= 1
    return round((total / 7)  * 100)

def get_admin_name(department):
    doc_ref = db.collection(EMPLOYER_COLLECTION).document('admin_info')
    doc = doc_ref.get().to_dict()
    return doc[department]
        
    
@app.route("/predict", methods=['GET'])
def predict():
    body = request.json
    id = body['id']
    doc_ref = db.collection(EMPLOYEE_COLLECTION).document(str(id))
    doc = doc_ref.get()

    inp = {
        'ID':0, 
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
        'hours':40
    }

    if doc.exists:
        employee_m = doc.to_dict()
        url = "https://us-central1-ieor185-274323.cloudfunctions.net/state_prediction?message=eydpbnAnOiB7J0lEJzogMCwgJ2FnZSc6IDIxLCAnZ2VuZGVyJzogJ21hbGUnLCAnYm9keV9mYXRfcGVyY2VudGFnZSc6IDEyLCAnaGVpZ2h0JzogMCwgJ3dlaWdodCc6IDAsICdudW1fYnJlYWtzJzogNSwgJ251bV90YXNrX3BlbmRpbmcnOiAyMzQsICdhdmVyYWdlX3Rhc2tfY29tcGxldGlvbl9kZWxheSc6IDAsICdjYWxvcmllc19lYXRlbic6IDAsICdtb3JuaW5nIHB1c2ggcGVyY2VudGFnZSc6IDAuMiwgJ2FmdGVybm9vbiBwdXNoIHBlcmNlbnRhZ2UnOiAwLjYsICdldmVuaW5nIHB1c2ggcGVyY2VudGFnZSc6IDAuMiwgJ2dpdF9hdmdfcHVzaF90aW1lX2RpZmZlcmVuY2UnOiAxMCwgJ2F2ZXJhZ2VfY2hhdF90b25lJzogJ0FuZ3J5JywgJ2VyZ29ub21pY19yaXNrX3JhdGluZyc6IDUsICdudW1iZXIgb2YgdGltZXMgc3RhbmRpbmcnOiAxLCAnbWludXRlc193b3JrZWRfb3V0JzogMCwgJ2F2ZXJhZ2VfaGVhcnRfcmF0ZSc6IDE4MCwgJ3RyYWZmaWMgY29uZGl0aW9uJzogJ1JlZCcsICdjaGF0LXdvcmRzJzogJ2JhZCcsICdsb2NhdGlvbic6ICc3NzQ5NCcsICd3b3JrcGxhY2UgdGVtcGVyYXR1cmUnOiAnMjMnLCAnd2VhdGhlcic6ICdyYWlueScsICdlbnRyeSB0aW1lJzogMywgJ2V4aXQgdGltZSc6IDMsICdzdG9ja190aWNrZXInOiAnR09PRycsICdzdG9jayc6IC0wLjAxLCAnaG91cnMnOiA0MH0sICduYW1lJzogJ2RlcHJlc3Npb24nfQ=="
        params = {
            'inp': employee_m,
            'name': 'depression'
        }
        r = requests.get(url, params)
        return r
    else:
        return f"Employee id does not exist"

# main
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
