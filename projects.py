from flask import Blueprint, request, jsonify, send_file
from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime
import os
from bson import ObjectId
from io import BytesIO

client = MongoClient('localhost', 27017)
db = client['prometheus']
projects_collection = db['projects']
fs = GridFS(db)

project_blueprint = Blueprint('project', __name__)

@project_blueprint.route('/projects', methods=['POST'])
def create_project():
    try:
        data = request.form.to_dict()
        image = request.files.get('image')
        
        required_fields = [
            "buildingName", "buildingAddress", "yearBuilt", "city",
            "state", "county", "zip", "grossSquareFootage", "floorPlate", 
            "efficiency", "unitSize", "unitsPerFloor", "floors", 
            "grossRent", "assumedVacancy", "operatingExpense", 
            "entryCapRate", "exitCapRate"
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        try:
            data['grossSquareFootage'] = float(data['grossSquareFootage'])
            data['floorPlate'] = float(data['floorPlate'])
            data['efficiency'] = float(data['efficiency'])
            data['unitSize'] = float(data['unitSize'])
            data['unitsPerFloor'] = float(data['unitsPerFloor'])
            data['floors'] = float(data['floors'])
            data['grossRent'] = float(data['grossRent'])
            data['assumedVacancy'] = float(data['assumedVacancy'])
            data['operatingExpense'] = float(data['operatingExpense'])
            data['entryCapRate'] = float(data['entryCapRate'])
            data['exitCapRate'] = float(data['exitCapRate'])
        except ValueError as e:
            return jsonify({"error": f"Invalid data type for numerical field: {str(e)}"}), 400
        
        efficiency_percentage = data['efficiency'] / 100
        assumed_vacancy_percentage = data['assumedVacancy'] / 100
        operating_expense_percentage = data['operatingExpense'] / 100
        data['netFloorPlate'] = data['floorPlate'] * efficiency_percentage
        data['netRentableSquareFootage'] = data['grossSquareFootage'] * efficiency_percentage
        data['unitFloors'] = data['floors'] - 2
        data['totalUnits'] = data['unitsPerFloor'] * data['unitFloors']
        data['netEffectiveRent'] = data['grossRent'] * (1 - assumed_vacancy_percentage)
        data['netOperatingIncome'] = data['netEffectiveRent'] * (1 - operating_expense_percentage)
        data['developmentYield'] = (data['netOperatingIncome'] / data['grossSquareFootage']) * 100
        data['datetimeCreated'] = datetime.now()
        
        if image:
            image_id = fs.put(image, filename=image.filename)
            data['image_id'] = image_id

        result = projects_collection.insert_one(data)
        return jsonify({"message": "Project created successfully", "id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_blueprint.route('/uploads/<id>')
def get_uploaded_file(id):
    try:
        grid_out = fs.get(ObjectId(id))
        return send_file(BytesIO(grid_out.read()), mimetype=grid_out.content_type, download_name=grid_out.filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500