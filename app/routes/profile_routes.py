from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User
import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()['id']
    user = db.session.get(User, user_id)  # Updated to use Session.get()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }
    
    return jsonify(user_data), 200

@bp.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    user_id = get_jwt_identity()['id']
    user = db.session.get(User, user_id)  # Updated to use Session.get()
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    fields_to_update = {key: value for key, value in data.items() if key in ['first_name', 'last_name'] and value}
    if fields_to_update:
        for key, value in fields_to_update.items():
            setattr(user, key, value)
        user.update_date = datetime.datetime.utcnow()
        db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200
