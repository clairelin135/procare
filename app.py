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
import datetime
from backend.models.prediction_retriever import get_state_prediction, get_health_prediction

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
ACTIONS_COLLECTION = "actions"

EMPLOYER_ROUTE = "/employer/"
EMPLOYEE_ROUTE = "/employee/"

# Useful dictionaries
db_m = {'1': 'engineering', '2': 'product-management', '3': 'sales'}
human_m = {'1': 'Engineering', '2': 'Product', '3': 'Sales'}

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

    for i in range(1, len(db_m)+1):
        name = human_m[str(i)]
        employer = {
            'name': name,
            'route': EMPLOYER_ROUTE + str(i)
        }
        employers.append(employer)

    return render_template("index.html", employees=employees, employers=employers)


@app.route(EMPLOYEE_ROUTE + '<id>', methods=['GET', 'POST'])
def employee(id):
    class F(Form):
        pass

    # Fetch nudges and add to document
    nudges = []
    point_count = 0
    nudges_ref = db.collection(NUDGE_COLLECTION + "-" + str(id)).stream()
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

        doc["water_percentage"] = round(round(doc["water_consumed"][0]["data"]/8, 2)*100)
        doc["focus_percentage"] = round(round(55/120, 2)*100)

        break_duration_len = min(32, len(doc["break_durations"]))
        x = []
        y = []
        for b in doc["break_durations"][-break_duration_len:]:
            x.append(b["time"])
            y.append(sum(b["data"]))

        doc["min_focused"] = sum(doc["focustimes"][len(doc["focustimes"]) - 1]["data"])
        doc["min_remaining"] = 15 - doc["min_focused"]
        doc["min_percentage"] = round(round(doc["min_focused"]/15, 2)*100)

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

@app.route(EMPLOYER_ROUTE + '<id>', methods=['GET', 'POST'])
def employer(id):
    department = db_m[id]

    emo_p = get_weekly_average(department, "emotional_level")
    pro_p = get_weekly_average(department, "productivity")
    phy_p = get_weekly_average(department, "physical_wellness")
    admin_name = get_attr(department, 'admin_info')
    attendance = get_attr(department, 'attendance')
    late = get_attr(department, 'late')
    absent = get_attr(department, 'absent')
    percentages = ill_percentages(department)
    top_illness = None
    top_perc = 0
    for k, v in percentages.items():
        if v > top_perc:
            top_perc = v
            top_illness = k
    if top_illness == 'ct':
        top_illness_name = 'Carpal Tunnel - Numbness/Tingling of the wrist'
    elif top_illness == 'depression':
        top_illness_name = 'Depression'
    elif top_illness == 'lombago':
        top_illness_name = 'Lombago - Lower back pain'

    doc = {'emotion-percentage': str(emo_p)+'%',
            'product-percentage': str(pro_p)+'%',
            'physical-percentage': str(phy_p)+'%',
            'attendance': attendance,
            'late': late,
            'absent': absent,
            'admin-name': admin_name,
            'dep-name': human_m[id],
            'top-illness': top_illness,
            'top-illness-name': top_illness_name,
            'depression': str(percentages['depression'])+'%',
            'ct': str(percentages['ct'])+'%',
            'lombago': str(percentages['lombago'])+'%'
        }
    depression_actions = {
        'action1-name': 'Send Nudges',
        'action1-description': 'ye',
        'action1-action': 'uhh onclick actions?',
        'action2-name': 'Meditation',
        'action2-description': 'sign up for meditating',
        'action2-action': 'uhh onclick actions?',
        'action3-name': 'Gym',
        'action3-description': 'yall fat',
        'action3-action': 'uhh onclick actions?'
    }

    actions_doc = db.collection(ACTIONS_COLLECTION).document(doc['top-illness']).get()
    if actions_doc.exists:
        actions = actions_doc.to_dict()
    else:
        actions = depression_actions

    x = get_x_axis()
    script_prod, div_prod = create_plot(x, 'productivity')
    script_em, div_em = create_plot(x, 'emotional_level')
    script_ph, div_ph = create_plot(x, 'physical_wellness')

    return render_template("employer.html", data=doc, actions=actions, script_prod=script_prod, div_prod=div_prod,
    script_em=script_em, div_em=div_em, script_ph=script_ph, div_ph=div_ph)

# deparatment: [product-management, engineering, sales]
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

def get_attr(department, attr):
    doc_ref = db.collection(EMPLOYER_COLLECTION).document(department)
    doc = doc_ref.get().to_dict()
    return doc[attr]

# retrieves the percentages of depression, ct, and lombago, given department
def ill_percentages(department):
    employee_docs = db.collection(EMPLOYEE_COLLECTION).stream()
    depression = 0
    ct = 0
    lombago = 0
    c = 0
    for doc in employee_docs:
        json_doc = doc.to_dict()
        if json_doc['department'] != department:
            continue
        depression += get_state_prediction(json_doc['id'], 'depression')
        ct += get_state_prediction(json_doc['id'], 'ct')
        lombago +=  get_state_prediction(json_doc['id'], 'lombago')
        c += 1
    return {'depression': round((depression / c) * 100), 'ct': round((ct / c) * 100), 'lombago': round((lombago / c) * 100)}

# stat: emotional_level, physical_wellness, productivity
# creates plot for all departments for one stat type
def create_plot(x, stat):
    y_axis_label = ""
    if stat == "productivity":
        y_axis_label = "Productivity"
    elif stat == "emotional_level":
        y_axis_label = "Emotional Wellness"
    elif stat == "physical_wellness":
        y_axis_label = "Physical Wellness"

    eng = []
    pm = []
    sal = []
    for date in x:
        for dept in ['engineering', 'product-management', 'sales']:
            doc_stream = db.collection(EMPLOYER_COLLECTION).document(date.strftime("%Y-%m-%d")).collection(dept).stream()
            for doc in doc_stream:
                json_doc = doc.to_dict()
                if dept == 'engineering':
                    eng.append(json_doc[stat])
                elif dept == 'product-management':
                    pm.append(json_doc[stat])
                elif dept == 'sales':
                    sal.append(json_doc[stat])

    p = figure(x_axis_type="datetime", y_range=(0, 1), plot_width=550, plot_height=300)
    p.line(x, eng, line_width=2, line_color="#8CCFBB", legend_label="Engineering") #eng is green
    p.line(x, pm, line_width=2, line_color="#eaadbd", legend_label="Product Management") #pm is pink
    p.line(x, sal, line_width=2, line_color="#ffa751", legend_label="Sales") #sales is orange
    p.legend.title = 'Departments'
    p.legend.location = 'bottom_right'
    p.legend.click_policy = 'hide'
    p.toolbar_location = None
    p.xaxis.axis_label = "Day"
    p.yaxis.axis_label = y_axis_label

    script, div = components(p)

    return script, div

def get_x_axis():
    day = 21
    x = []
    for _ in range(7):
        #date = "2020-04-" + str(day)
        x.insert(0, datetime.datetime(2020, 4, day))
        day -= 1
    return x

# main
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
