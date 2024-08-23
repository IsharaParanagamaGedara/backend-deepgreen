import sys
import os

# Ensure the project root is on the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User
from app.config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)  # Pass TestingConfig to create_app
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token(client):
    user = User(email="test@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    return response.json['access_token']
