from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson.json_util import dumps

login_bp = Blueprint('signin', __name__)

client = MongoClient('localhost', 27017)
db = client['prometheus']
users_collection = db['users']

@login_bp.route('/signin', methods=['POST'])
def signin():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')

    user = users_collection.find_one({
        "$or": [{"user": identifier}, {"email": identifier}],
        "password": password  
    })

    if user:
        session['user_id'] = str(user['_id'])
        session.modified = True  # Ensure session is marked as modified
        return jsonify({"message": "passed", "user": dumps(user)}), 200
    else:
        return jsonify({"message": "Invalid identifier or password"}), 401

@login_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@login_bp.route('/status')
def status():
    if 'user_id' in session:
        return jsonify({"authenticated": True, "user_id": session['user_id']}), 200
    return jsonify({"authenticated": False}), 200
