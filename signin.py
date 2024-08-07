from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from bson.json_util import dumps
from pymongo.server_api import ServerApi
import ssl

uri = "mongodb+srv://stevefelizardo4:Pufqe1LOw6lOLMH0@prometheus.ujykcdq.mongodb.net/?retryWrites=true&w=majority&appName=Prometheus"

login_bp = Blueprint('signin', __name__)

try:
    client = MongoClient(uri, server_api=ServerApi('1'), ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
    db = client['prometheus']
    users_collection = db['users']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

@login_bp.route('/signin', methods=['POST'])
def signin():
    try:
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
    except Exception as e:
        print(f"Error in signin: {e}")
        return jsonify({"message": "An error occurred"}), 500

@login_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.pop('user_id', None)
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        print(f"Error in logout: {e}")
        return jsonify({"message": "An error occurred"}), 500

@login_bp.route('/status')
def status():
    try:
        if 'user_id' in session:
            return jsonify({"authenticated": True, "user_id": session['user_id']}), 200
        return jsonify({"authenticated": False}), 200
    except Exception as e:
        print(f"Error in status: {e}")
        return jsonify({"message": "An error occurred"}), 500
