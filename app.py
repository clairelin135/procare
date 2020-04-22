# app.py
# Required Imports
import os
import json
import pyrebase
from flask import Flask, request, jsonify, render_template, url_for
from firebase_admin import credentials, firestore, initialize_app

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

# firebase = pyrebase.initialize_app(config)
# db  = firebase.database()
# db.child("names").push({
#     "name": "Elden"
# })

# Initialize Flask App
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client() 

# given collection, and document, adds an name/age entry into db
@app.route('/add', methods=['POST'])
def create_employee():
    try:
        body = request.json
        id = body['id']
        collection = body['collection']
        document = body['document']
        name = body["name"]
        age = body["age"]

        doc_ref = db.collection(collection).document(document+str(id))
        doc_ref.set({
            "name": name,
            "age": age
        })
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

# returns the requested 
# json req keys: id, collection, document, field
@app.route('/list', methods=['GET'])
def read_employee_info():
    try:
        body = request.json
        id = body['id']
        collection = body['collection']
        document = body['document']
        doc_ref = db.collection(collection).document(document+str(id))
        doc = doc_ref.get()

        if doc.exists:
            doc = doc.to_dict()
            return jsonify({
                'name': doc['name'],
                'age': doc['age']
            })
    except Exception as e:
        return f"An Error Occured: {e}"

# updates an employee field
# json req requires: id, collection, document, field, update
@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        body = request.json
        id = body['id']
        collection = body['collection']
        document = body['document']
        doc_ref = db.collection(collection).document(document+str(id))
        doc_ref.update({body['field']: body['update']})
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


# delete an employee
# json requires: id
@app.route('/delete', methods=['GET'])
def delete_employee():
    """
        delete() : Delete a document from Firestore collection
    """
    try:
        # Check for ID in URL query
        body = request.json
        id = body['id']
        doc_ref = db.collection('employees').document('employee'+str(id))
        doc_ref.delete()
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/') 
# ‘/’ URL is bound with hello_world() function. 
def hello_world(): 
    return 'Hello World'

@app.route('/employee/<id>')
def employee(id):
    collection = "employees"
    document = "employee"

    doc_ref = db.collection(collection).document(document+str(id))
    doc = doc_ref.get()

    if doc.exists:
        doc = doc.to_dict()
        doc["water_percentage"] = round(round(doc["water_consumed"]/doc["water_dv"], 2)*100)
        doc["focus_percentage"] = round(round(doc["time_focused"]/120, 2)*100)
        return render_template("employee.html", data=doc)
    else:
        return f"An Error Occured: {e}"
  
# main
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
