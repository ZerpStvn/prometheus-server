import ssl
from bson import ObjectId
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://stevefelizardo4:Pufqe1LOw6lOLMH0@prometheus.ujykcdq.mongodb.net/?retryWrites=true&w=majority&appName=Prometheus"

get_project = Blueprint('getproject', __name__)
client = MongoClient(
    uri,
    # Optional parameters
    document_class=dict,
    tz_aware=True,
    connect=True,
    server_api=ServerApi('1'),
    tls=True,
    tlsAllowInvalidCertificates=True, 
)
db = client['prometheus']
projects_collection = db['projects']
assumptions_collection = db['assumptions']

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
            assumptions = assumptions_collection.find_one({"project_id": id})
            if assumptions:
                project['assumptions'] = assumptions['assumptions']
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

# assumptions
@get_project.route('/save_assumptions/<project_id>', methods=['POST'])
def save_assumptions(project_id):
    try:
        assumptions = request.json.get('assumptions', {})
        existing_assumption = assumptions_collection.find_one({"project_id": project_id})
        if existing_assumption:
            assumptions_collection.update_one(
                {"project_id": project_id},
                {"$set": {"assumptions": assumptions}}
            )
        else:
            assumptions_collection.insert_one({
                "project_id": project_id,
                "assumptions": assumptions
            })
        return jsonify({"message": "Assumptions saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@get_project.route('/get_assumptions/<project_id>', methods=['GET'])
def get_assumptions(project_id):
    try:
        assumptions = assumptions_collection.find_one({"project_id": project_id})
        if assumptions:
            return jsonify(assumptions['assumptions']), 200
        else:
            return jsonify({"error": "Assumptions not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
