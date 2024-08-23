from flask import Blueprint, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Prediction, Image
import os
from sqlalchemy import func, case

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()['id']
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }
    
    return jsonify(user_data), 200

@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    user_id = get_jwt_identity()['id']
    
    # Query for total number of predictions
    total_predictions = db.session.query(Prediction).filter_by(user_id=user_id).count()
    
    # Query for total number of healthy predictions
    healthy_predictions = db.session.query(Prediction).filter_by(user_id=user_id).filter(
        Prediction.predicted_class.like('%healthy%')
    ).count()
    
    # Query for total number of diseased plants (excluding healthy and unknown classes)
    diseased_predictions = db.session.query(Prediction).filter_by(user_id=user_id).filter(
        ~Prediction.predicted_class.like('%healthy%'),
        ~Prediction.predicted_class.like('%Unknown%')
    ).count()

    return jsonify({
        'predictions_made': total_predictions,
        'healthy_plants': healthy_predictions,
        'diseased_plants': diseased_predictions
    }), 200

@bp.route('/recent_activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    user_id = get_jwt_identity()['id']
    
    # Query for the two most recent predictions
    recent_predictions = db.session.query(
        Prediction.id,
        Prediction.image_id,
        Prediction.predicted_class,
        Prediction.confidence_percentage,
        Prediction.prediction_date,
        Image.image_path
    ).join(Image, Prediction.image_id == Image.id).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.prediction_date.desc()).limit(3).all()
    
    recent_activities = []
    for prediction in recent_predictions:
        recent_activities.append({
            'id': prediction.id,
            'image_id': prediction.image_id,
            'predicted_class': prediction.predicted_class,
            'confidence_percentage': prediction.confidence_percentage,
            'prediction_date': prediction.prediction_date,
            'image_url': url_for('uploaded_file', filename=os.path.basename(prediction.image_path), _external=True)
        })

    return jsonify(recent_activities), 200

@bp.route('/predictions_by_crop_type', methods=['GET'])
@jwt_required()
def get_predictions_by_crop_type():
    user_id = get_jwt_identity()['id']

    # Define crop categories
    crop_types = {
        'Corn': ['Corn___Common_rust', 'Corn___Gray_leaf_spot', 'Corn___Northern_Leaf_Blight', 'Corn___healthy'],
        'Potato': ['Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy'],
        'Strawberry': ['Strawberry___Leaf_scorch', 'Strawberry___healthy'],
        'Unknown': ['Unknown___Unexpected_input']
    }

    # Initialize dictionary to count predictions per crop type
    crop_type_counts = {
        'Corn': 0,
        'Potato': 0,
        'Strawberry': 0,
        'Unknown': 0
    }

    # Query predictions for the user
    predictions = db.session.query(Prediction.predicted_class).filter_by(user_id=user_id).all()

    # Count predictions per crop type
    for prediction in predictions:
        for crop, classes in crop_types.items():
            if prediction.predicted_class in classes:
                crop_type_counts[crop] += 1
                break

    # Calculate total predictions
    total_predictions = sum(crop_type_counts.values())

    if total_predictions == 0:
        crop_type_percentages = {crop: 0 for crop in crop_type_counts}
    else:
        # Calculate prediction percentages
        crop_type_percentages = {crop: (count / total_predictions) * 100 for crop, count in crop_type_counts.items()}

    return jsonify({
        'crop_type_counts': crop_type_counts,
        'crop_type_percentages': crop_type_percentages
    }), 200

