from flask import Blueprint, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Prediction, Image, UserSatisfactionSurvey
import os
from sqlalchemy import func, case
import datetime
from collections import Counter
import numpy as np
import logging

bp = Blueprint('stat', __name__, url_prefix='/stat')

@bp.route('/overview/all', methods=['GET'])
@jwt_required()
def get_prediction_overview_all():
    # Query for total number of predictions
    total_predictions = db.session.query(Prediction).count()
    
    # Query for total number of healthy predictions
    healthy_predictions = db.session.query(Prediction).filter(
        Prediction.predicted_class.like('%healthy%')
    ).count()
    
    # Query for total number of diseased plants (excluding healthy and unknown classes)
    diseased_predictions = db.session.query(Prediction).filter(
        ~Prediction.predicted_class.like('%healthy%'),
        ~Prediction.predicted_class.like('%Unknown%')
    ).count()

    return jsonify({
        'predictions_made': total_predictions,
        'healthy_plants': healthy_predictions,
        'diseased_plants': diseased_predictions
    }), 200


@bp.route('/charts/number_of_predictions_per_class', methods=['GET'])
@jwt_required()
def get_number_of_predictions_per_class():
    user_id = get_jwt_identity()['id']
    
    predictions_per_class = db.session.query(
        Prediction.predicted_class, func.count(Prediction.id)
    ).filter(
        Prediction.user_id == user_id
    ).group_by(Prediction.predicted_class).all()
    
    data = {
        "classes": [result[0] for result in predictions_per_class],
        "counts": [result[1] for result in predictions_per_class]
    }
    
    return jsonify(data), 200


@bp.route('/charts/predictions_over_time', methods=['GET'])
@jwt_required()
def get_predictions_over_time():
    user_id = get_jwt_identity()['id']
    
    predictions_over_time = db.session.query(
        func.date_format(Prediction.prediction_date, '%Y-%m-%d').label('date'),
        func.count(Prediction.id)
    ).filter(
        Prediction.user_id == user_id
    ).group_by('date').order_by('date').all()
    
    data = {
        "dates": [result[0] for result in predictions_over_time],
        "counts": [result[1] for result in predictions_over_time]
    }
    
    return jsonify(data), 200


@bp.route('/charts/confidence_percentage_distribution', methods=['GET'])
@jwt_required()
def get_confidence_percentage_distribution():
    user_id = get_jwt_identity()['id']
    
    confidence_percentages = db.session.query(
        Prediction.confidence_percentage
    ).filter(
        Prediction.user_id == user_id
    ).all()
    
    # Extract confidence percentages from the query results
    confidence_values = [result[0] for result in confidence_percentages]
    
    # Create bins for confidence percentage ranges (0-10, 11-20, ..., 91-100)
    bins = [i for i in range(0, 101, 10)]
    frequency = [0] * len(bins)  # Initialize frequency with the number of bins
    
    for confidence in confidence_values:
        bin_index = int(confidence // 10)
        if bin_index < len(bins):  # Ensure bin_index is within range
            frequency[bin_index] += 1
    
    data = {
        "bins": bins,
        "frequency": frequency
    }
    
    return jsonify(data), 200


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    try:
        # Calculate satisfaction statistics
        satisfaction_stats = db.session.query(
            UserSatisfactionSurvey.satisfaction,
            func.count(UserSatisfactionSurvey.satisfaction)
        ).group_by(UserSatisfactionSurvey.satisfaction).all()

        # Calculate recommendation statistics
        recommendation_stats = db.session.query(
            UserSatisfactionSurvey.recommendation,
            func.count(UserSatisfactionSurvey.recommendation)
        ).group_by(UserSatisfactionSurvey.recommendation).all()

        # Calculate usefulness statistics
        usefulness_stats = db.session.query(
            UserSatisfactionSurvey.usefulness
        ).all()

        # Calculate desired features statistics
        desired_features_stats = db.session.query(
            UserSatisfactionSurvey.desired_features
        ).all()

        # Convert statistics to a dictionary
        satisfaction_dict = {stat[0]: stat[1] for stat in satisfaction_stats}
        recommendation_dict = {stat[0]: stat[1] for stat in recommendation_stats}

        # Process usefulness and desired features (comma-separated strings)
        usefulness_dict = {}
        for entry in usefulness_stats:
            features = entry.usefulness.split(',')
            for feature in features:
                if feature in usefulness_dict:
                    usefulness_dict[feature] += 1
                else:
                    usefulness_dict[feature] = 1

        desired_features_dict = {}
        for entry in desired_features_stats:
            features = entry.desired_features.split(',')
            for feature in features:
                if feature in desired_features_dict:
                    desired_features_dict[feature] += 1
                else:
                    desired_features_dict[feature] = 1

        # Calculate total counts for usefulness and desired features
        total_usefulness = sum(usefulness_dict.values())
        total_desired_features = sum(desired_features_dict.values())

        # Calculate percentages for usefulness
        usefulness_percentage_dict = {
            feature: (count / total_usefulness) * 100 for feature, count in usefulness_dict.items()
        }

        # Calculate percentages for desired features
        desired_features_percentage_dict = {
            feature: (count / total_desired_features) * 100 for feature, count in desired_features_dict.items()
        }

        return jsonify({
            "satisfaction": satisfaction_dict,
            "recommendation": recommendation_dict,
            "usefulness": usefulness_percentage_dict,
            "desiredFeatures": desired_features_percentage_dict
        }), 200
    except Exception as e:
        logging.error(f"Error fetching survey statistics: {e}")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
