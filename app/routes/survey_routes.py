import json
from sqlalchemy import func, case
from flask import Blueprint, request, jsonify
from app.models import UserSatisfactionSurvey
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

bp = Blueprint('survey', __name__, url_prefix='/survey')

@bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_survey():
    try:
        user_info = get_jwt_identity()
        user_id = user_info['id']  # Extract user_id from the dictionary

        data = request.get_json()

        # Convert lists to comma-separated strings
        usefulness = ','.join(data['usefulness'])
        desired_features = ','.join(data['desiredFeatures'])

        # Check if a survey already exists for the user
        existing_survey = UserSatisfactionSurvey.query.filter_by(user_id=user_id).first()

        if existing_survey:
            # Update the existing survey
            existing_survey.satisfaction = data['satisfaction']
            existing_survey.usefulness = usefulness
            existing_survey.desired_features = desired_features
            existing_survey.recommendation = data['recommendation']
            db.session.commit()
            return jsonify({"message": "Survey updated successfully!"}), 200
        else:
            # Create a new survey
            new_survey = UserSatisfactionSurvey(
                user_id=user_id,
                satisfaction=data['satisfaction'],
                usefulness=usefulness,
                desired_features=desired_features,
                recommendation=data['recommendation']
            )
            db.session.add(new_survey)
            db.session.commit()
            return jsonify({"message": "Survey submitted successfully!"}), 201
    except Exception as e:
        logging.error(f"Error submitting survey: {e}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
