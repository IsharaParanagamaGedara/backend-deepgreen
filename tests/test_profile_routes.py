import pytest
from app import create_app, db
from app.models import User
from app.config import TestingConfig
import datetime
from flask import jsonify
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

@pytest.fixture
def app():
    app = create_app(TestingConfig)
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
    hashed_password = bcrypt.generate_password_hash("password").decode('utf-8')
    user = User(email="test@example.com", password=hashed_password, first_name="Test", last_name="User")
    db.session.add(user)
    db.session.commit()
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    token = response.get_json().get('token')
    return token

def test_get_profile(client, token):
    response = client.get('/profile/', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data['first_name'] == "Test"
    assert user_data['last_name'] == "User"
    assert user_data['email'] == "test@example.com"

def test_update_profile(client, token):
    update_data = {
        "first_name": "UpdatedTest",
        "last_name": "UpdatedUser"
    }
    response = client.put('/profile/update_profile', json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()['message'] == "Profile updated successfully"
    
    # Verify the update in the database
    response = client.get('/profile/', headers={"Authorization": f"Bearer {token}"})
    user_data = response.get_json()
    assert user_data['first_name'] == "UpdatedTest"
    assert user_data['last_name'] == "UpdatedUser"

def test_get_profile_user_not_found(client, token):
    # Simulate user not found by deleting the user
    User.query.delete()
    db.session.commit()

    response = client.get('/profile/', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.get_json()['message'] == "User not found"

def test_update_profile_user_not_found(client, token):
    # Simulate user not found by deleting the user
    User.query.delete()
    db.session.commit()

    update_data = {
        "first_name": "UpdatedTest",
        "last_name": "UpdatedUser"
    }
    response = client.put('/profile/update_profile', json=update_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.get_json()['message'] == "User not found"
