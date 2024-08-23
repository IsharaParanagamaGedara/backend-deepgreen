from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads'))
    SECRET_KEY = os.getenv('SECRET_KEY')

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MAIL_SUPPRESS_SEND = True
    JWT_SECRET_KEY = 'testing_jwt_secret_key'
    SECRET_KEY = 'testing_secret_key'