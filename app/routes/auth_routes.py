from flask import Blueprint, request, jsonify, url_for, current_app
from flask_mail import Message
from app import db, bcrypt, mail
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from flask_jwt_extended import jwt_required, create_access_token, get_jwt, JWTManager
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize the JWT manager
jwt = JWTManager()

# In-memory store for revoked tokens
revoked_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in revoked_tokens

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, ""

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ('first_name', 'last_name', 'email', 'password')):
        return jsonify(error="Missing data"), 400

    email = data['email']
    if User.query.filter_by(email=email).first():
        return jsonify(error="Email already registered"), 400

    password_valid, password_message = validate_password(data['password'])
    if not password_valid:
        return jsonify(error=password_message), 400

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(first_name=data['first_name'], last_name=data['last_name'], email=email, password=hashed_password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User registered successfully"), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during registration: {str(e)}")
        return jsonify(error="Registration failed. Please try again."), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify(error="Missing data"), 400

    email = data['email']
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'id': user.id, 'email': user.email})
        return jsonify({'token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200

s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(error="Missing email"), 400

    user = User.query.filter_by(email=data['email']).first()
    if user:
        token = s.dumps(user.email, salt='email-confirm')
        reset_url = f"http://localhost:3000/reset-password/{token}"  # Adjust the URL to your frontend
        msg = Message('Password Reset Request', recipients=[user.email])
        msg.body = f'Please click the link to reset your password: {reset_url}'
        try:
            mail.send(msg)
            return jsonify(message="Password reset email sent"), 200
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            return jsonify(error="Failed to send email"), 500

    return jsonify(error="Email not found"), 404

@bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception as e:
        current_app.logger.error(f"Token error: {str(e)}")
        return jsonify(error="Invalid or expired token"), 400

    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify(error="Missing password"), 400

    user = User.query.filter_by(email=email).first()
    if user:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_password
        try:
            db.session.commit()
            return jsonify(message="Password has been reset"), 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error resetting password: {str(e)}")
            return jsonify(error="Failed to reset password"), 500

    return jsonify(error="User not found"), 404
