import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from app.config import Config
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # Import routes and blueprints
    with app.app_context():
        from app.routes import (
            auth_routes, image_routes, prediction_routes, 
            profile_routes, suggestion_routes, disease_routes, 
            history_routes, survey_routes, dashboard_routes, stat_routes
        )
        app.register_blueprint(auth_routes.bp, url_prefix='/auth')
        app.register_blueprint(image_routes.bp, url_prefix='/image')
        app.register_blueprint(prediction_routes.bp, url_prefix='/prediction')
        app.register_blueprint(profile_routes.bp, url_prefix='/profile')
        app.register_blueprint(suggestion_routes.bp, url_prefix='/suggestion')
        app.register_blueprint(disease_routes.bp, url_prefix='/disease')
        app.register_blueprint(history_routes.bp, url_prefix='/history')
        app.register_blueprint(survey_routes.bp, url_prefix='/survey')
        app.register_blueprint(dashboard_routes.bp, url_prefix='/dashboard')
        app.register_blueprint(stat_routes.bp, url_prefix='/stat')
    
        # Create database tables
        db.create_all()

        # Insert initial data
        from app.models import insert_initial_data
        insert_initial_data()
        

    # Route for serving static files
    @app.route('/static/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app
