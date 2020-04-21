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

# given collection, and document, adds an entry into db
@app.route('/add', methods=['GET', 'POST'])
def create():
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

# @app.route('/list', methods=['GET'])
# def read():
#     """
#         read() : Fetches documents from Firestore collection as JSON
#         todo : Return document that matches query ID
#         all_todos : Return all documents
#     """
#     try:
#         # Check if ID was passed to URL query
#         todo_id = request.args.get('id')    
#         if todo_id:
#             todo = todo_ref.document(todo_id).get()
#             return jsonify(todo.to_dict()), 200
#         else:
#             all_todos = [doc.to_dict() for doc in todo_ref.stream()]
#             return jsonify(all_todos), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"

# @app.route('/update', methods=['POST', 'PUT'])
# def update():
#     """
#         update() : Update document in Firestore collection with request body
#         Ensure you pass a custom ID as part of json body in post request
#         e.g. json={'id': '1', 'title': 'Write a blog post today'}
#     """
#     try:
#         id = request.json['id']
#         todo_ref.document(id).update(request.json)
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"


# @app.route('/delete', methods=['GET', 'DELETE'])
# def delete():
#     """
#         delete() : Delete a document from Firestore collection
#     """
#     try:
#         # Check for ID in URL query
#         todo_id = request.args.get('id')
#         todo_ref.document(todo_id).delete()
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"

# The route() function of the Flask class is a decorator,  
# which tells the application which URL should call  
# the associated function. 
@app.route('/') 
# ‘/’ URL is bound with hello_world() function. 
def hello_world(): 
    return 'Hello World'

@app.route('/employee/<id>')
def employee(id):
    data = {
        'name': 'Claire',
    }
    return render_template("employee.html", data=data)
  
# main
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
