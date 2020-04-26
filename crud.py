from flask import Flask, request

# given collection, and document, adds an name/age entry into db
# @app.route('/add', methods=['POST'])
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
# @app.route('/list', methods=['GET'])
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
# @app.route('/update', methods=['POST', 'PUT'])
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
# @app.route('/delete', methods=['GET'])
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