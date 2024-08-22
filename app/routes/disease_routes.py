from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import PlantDisease

bp = Blueprint('disease', __name__)

@bp.route('/disease_names', methods=['GET'])
@jwt_required()
def get_disease_names():
    diseases = PlantDisease.query.with_entities(PlantDisease.disease_name).all()
    disease_names = [d.disease_name for d in diseases]
    return jsonify(disease_names), 200

@bp.route('/disease_info/<disease_name>', methods=['GET'])
@jwt_required()
def get_disease_info(disease_name):
    disease = PlantDisease.query.filter_by(disease_name=disease_name).first()
    if not disease:
        return jsonify({'message': 'Disease not found'}), 404

    disease_info = {
        'id': disease.id,
        'plant_name': disease.plant_name,
        'disease_name': disease.disease_name,
        'description': disease.description,
        'symptoms': disease.symptoms,
        'causes': disease.causes
    }
    return jsonify(disease_info), 200
