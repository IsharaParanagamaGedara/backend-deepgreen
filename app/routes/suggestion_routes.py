from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models import CureSuggestion, PlantDisease

bp = Blueprint('suggestion', __name__)

@bp.route('/detailed_cure_suggestions', methods=['GET'])
@jwt_required()
def detailed_cure_suggestions():
    disease_name = request.args.get('disease_name')
    if not disease_name:
        return jsonify({'message': 'Disease name is required'}), 400

    disease = PlantDisease.query.filter_by(disease_name=disease_name).first()
    if not disease:
        return jsonify({'message': 'Disease not found'}), 404

    suggestions = CureSuggestion.query.filter_by(disease_id=disease.id).all()
    if not suggestions:
        return jsonify({'message': 'No cure suggestions found for this disease'}), 404

    suggestions_list = [{'id': s.id, 'suggestion': s.suggestion} for s in suggestions]
    return jsonify(suggestions_list), 200
