from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Image
import os
from werkzeug.utils import secure_filename
import uuid
import logging

bp = Blueprint('image', __name__)

def save_image(file):
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)

    if os.path.exists(filepath):
        logging.info(f"File saved successfully: {filepath}")
    else:
        logging.error(f"File not found after saving: {filepath}")

    return filepath

@bp.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    user_id = get_jwt_identity()['id']
    try:
        filepath = save_image(file)
        image_record = Image(user_id=user_id, image_path=filepath)
        db.session.add(image_record)
        db.session.commit()
        logging.info(f"Image saved at: {filepath}")
        return jsonify({'message': 'Image uploaded successfully', 'image_id': image_record.id, 'file_path': filepath}), 201
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return jsonify({'message': 'Image upload failed', 'error': str(e)}), 500
