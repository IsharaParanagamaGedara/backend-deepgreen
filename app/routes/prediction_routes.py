from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app import db
from app.models import Image, Prediction
from app.utils.model_utils import predict_disease
import os
import logging

bp = Blueprint('prediction', __name__)

@bp.route('/predict_disease/<int:image_id>', methods=['GET'])
@jwt_required()
def predict_disease_route(image_id):
    image_record = Image.query.get(image_id)
    if not image_record:
        logging.warning(f"Image with ID {image_id} not found.")
        return jsonify({'message': 'Image not found'}), 404
    
    image_path = image_record.image_path
    logging.info(f"Predicting disease for image path: {image_path}")
    
    try:
        predicted_class, confidence_percentage = predict_disease(image_path)
        
        prediction = Prediction(
            user_id=image_record.user_id, 
            image_id=image_id, 
            predicted_class=predicted_class, 
            confidence_percentage=confidence_percentage
        )
        db.session.add(prediction)
        db.session.commit()
        
        # Generate the image URL
        filename = os.path.basename(image_path)
        image_url = f'/static/uploads/{filename}'
        logging.info(f"Generated image URL: {image_url}")
        
        response = {
            'prediction_id': prediction.id,
            'predicted_class': predicted_class,
            'confidence_percentage': confidence_percentage,
            'image_url': image_url
        }
        
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return jsonify({'message': 'Prediction failed', 'error': str(e)}), 500
