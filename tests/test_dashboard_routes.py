import pytest
from app import create_app, db
from app.models import User, Prediction, Image
from app.config import TestingConfig
from flask_jwt_extended import create_access_token
from datetime import datetime

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
    user = User(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        password="password"
    )
    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity={'id': user.id})
    return access_token

def test_get_profile(client, token):
    response = client.get('/dashboard/', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['first_name'] == "Test"
    assert data['last_name'] == "User"
    assert data['email'] == "testuser@example.com"

def test_get_dashboard_overview(client, token):
    user = User.query.first()
    
    # Add some predictions for the user
    prediction1 = Prediction(
        user_id=user.id,
        predicted_class='Tomato___healthy',
        confidence_percentage=95.0,
        prediction_date=datetime(2024, 7, 15, 14, 30, 0)
    )
    prediction2 = Prediction(
        user_id=user.id,
        predicted_class='Tomato___Early_blight',
        confidence_percentage=85.0,
        prediction_date=datetime(2024, 7, 16, 10, 0, 0)
    )
    db.session.add_all([prediction1, prediction2])
    db.session.commit()

    response = client.get('/dashboard/overview', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['predictions_made'] == 2
    assert data['healthy_plants'] == 1
    assert data['diseased_plants'] == 1

def test_get_recent_activity(client, token):
    user = User.query.first()
    
    # Add some predictions and images for the user
    image = Image(image_path='/path/to/image.jpg')
    db.session.add(image)
    db.session.commit()

    prediction1 = Prediction(
        user_id=user.id,
        image_id=image.id,
        predicted_class='Tomato___healthy',
        confidence_percentage=95.0,
        prediction_date=datetime(2024, 7, 15, 14, 30, 0)
    )
    prediction2 = Prediction(
        user_id=user.id,
        image_id=image.id,
        predicted_class='Tomato___Early_blight',
        confidence_percentage=85.0,
        prediction_date=datetime(2024, 7, 16, 10, 0, 0)
    )
    prediction3 = Prediction(
        user_id=user.id,
        image_id=image.id,
        predicted_class='Tomato___Late_blight',
        confidence_percentage=80.0,
        prediction_date=datetime(2024, 7, 17, 10, 0, 0)
    )
    db.session.add_all([prediction1, prediction2, prediction3])
    db.session.commit()

    response = client.get('/dashboard/recent_activity', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]['predicted_class'] == 'Tomato___Late_blight'
    assert data[1]['predicted_class'] == 'Tomato___Early_blight'
    assert data[2]['predicted_class'] == 'Tomato___healthy'
