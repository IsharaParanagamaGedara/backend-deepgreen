import pytest
from app import create_app, db
from app.models import User, UserSatisfactionSurvey
from app.config import TestingConfig
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Create a sample user
        user = User(email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token(client):
    access_token = create_access_token(identity={'id': 1})
    return access_token

def test_submit_survey_new(client, token):
    data = {
        "satisfaction": "Very satisfied",
        "usefulness": ["Uploading images of plant leaves", "Receiving disease predictions with confidence levels"],
        "desiredFeatures": ["More detailed prediction reports", "Better image upload interface"],
        "recommendation": "Very likely"
    }
    response = client.post('/survey/submit', headers={"Authorization": f"Bearer {token}"}, json=data)
    assert response.status_code == 201
    assert response.get_json()['message'] == "Survey submitted successfully!"

    # Check if the survey was added to the database
    survey = UserSatisfactionSurvey.query.filter_by(user_id=1).first()
    assert survey is not None
    assert survey.satisfaction == "Very satisfied"
    assert survey.usefulness == 'Uploading images of plant leaves,Receiving disease predictions with confidence levels'
    assert survey.desired_features == 'More detailed prediction reports,Better image upload interface'
    assert survey.recommendation == "Very likely"

def test_submit_survey_update(client, token):
    # Add an existing survey
    existing_survey = UserSatisfactionSurvey(
        user_id=1,
        satisfaction="Satisfied",
        usefulness='Feature1',
        desired_features='FeatureA',
        recommendation="Likely"
    )
    db.session.add(existing_survey)
    db.session.commit()

    # Update the survey
    data = {
        "satisfaction": "Very satisfied",
        "usefulness": ["Uploading images of plant leaves", "Receiving disease predictions with confidence levels"],
        "desiredFeatures": ["More detailed prediction reports", "Better image upload interface"],
        "recommendation": "Very likely"
    }
    response = client.post('/survey/submit', headers={"Authorization": f"Bearer {token}"}, json=data)
    assert response.status_code == 200
    assert response.get_json()['message'] == "Survey updated successfully!"

    # Check if the survey was updated in the database
    survey = UserSatisfactionSurvey.query.filter_by(user_id=1).first()
    assert survey is not None
    assert survey.satisfaction == "Very satisfied"
    assert survey.usefulness == 'Uploading images of plant leaves,Receiving disease predictions with confidence levels'
    assert survey.desired_features == 'More detailed prediction reports,Better image upload interface'
    assert survey.recommendation == "Very likely"

def test_submit_survey_missing_data(client, token):
    data = {
        "satisfaction": "Very satisfied",
        "usefulness": ["Uploading images of plant leaves", "Receiving disease predictions with confidence levels"]
        # 'desiredFeatures' and 'recommendation' are missing
    }
    response = client.post('/survey/submit', headers={"Authorization": f"Bearer {token}"}, json=data)
    assert response.status_code == 500
    assert "An error occurred" in response.get_json()['message']
