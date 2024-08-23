import pytest
from app import create_app, db
from app.models import User, Prediction, UserSatisfactionSurvey
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

def test_get_prediction_overview_all(client, token):
    user = User.query.first()
    # Add some predictions
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

    response = client.get('/stat/overview/all', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['predictions_made'] == 2
    assert data['healthy_plants'] == 1
    assert data['diseased_plants'] == 1

def test_get_number_of_predictions_per_class(client, token):
    user = User.query.first()
    # Add some predictions
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

    response = client.get('/stat/charts/number_of_predictions_per_class', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert sorted(data['classes']) == sorted(['Tomato___healthy', 'Tomato___Early_blight'])
    assert sorted(data['counts']) == sorted([1, 1])


