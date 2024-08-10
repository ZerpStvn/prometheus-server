import ssl
from bson import ObjectId
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://stevefelizardo4:Pufqe1LOw6lOLMH0@prometheus.ujykcdq.mongodb.net/?retryWrites=true&w=majority&appName=Prometheus"

get_project = Blueprint('getproject', __name__)
client = MongoClient(uri,ssl=True,
    ssl_cert_reqs=ssl.CERT_NONE, server_api=ServerApi('1'))
db = client['prometheus']
projects_collection = db['projects']

@get_project.route('/getprojects', methods=['GET'])
def get_projects():
    try:
        projects = list(projects_collection.find())
        for project in projects:
            project['_id'] = str(project['_id'])
            if 'image_id' in project:
                project['image_id'] = str(project['image_id'])
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@get_project.route('/getprojects/<id>', methods=['GET'])
def get_project_by_id(id):
    try:
        project = projects_collection.find_one({"_id": ObjectId(id)})
        if project:
            project['_id'] = str(project['_id'])
            if 'image_id' in project:
                project['image_id'] = str(project['image_id'])
            return jsonify(project), 200
        else:
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@get_project.route('/getprojects/edit/<id>', methods=['PUT'])
def update_project(id):
    try:
        data = request.json
        projects_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        return jsonify({"message": "Project updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@get_project.route('/getprojects/delete/<id>', methods=['DELETE'])
def delete_project(id):
    try:
        projects_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Project deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
