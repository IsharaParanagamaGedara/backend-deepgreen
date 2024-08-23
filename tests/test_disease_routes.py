import pytest
from app import create_app, db
from app.models import PlantDisease
from app.config import TestingConfig
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Add sample data
        disease1 = PlantDisease(
            plant_name="Strawberry",
            disease_name="Strawberry___Leaf_scorch",
            description="Leaf scorch is a fungal disease affecting strawberry leaves.",
            symptoms="Irregular, brown, and dead areas on leaves, often with a yellow halo.",
            causes="Caused by the fungus Diplocarpon earliana."
        )
        disease2 = PlantDisease(
            plant_name="Strawberry",
            disease_name="Strawberry___healthy",
            description="This is a healthy strawberry plant with no diseases.",
            symptoms="No symptoms.",
            causes="No causes."
        )
        db.session.add(disease1)
        db.session.add(disease2)
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

def test_get_disease_names_success(client, token):
    response = client.get('/disease/disease_names', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Response: {response.data}"
    response_data = response.get_json()
    assert "Strawberry___Leaf_scorch" in response_data
    assert "Strawberry___healthy" in response_data

def test_get_disease_info_success(client, token):
    response = client.get('/disease/disease_info/Strawberry___Leaf_scorch', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data['disease_name'] == 'Strawberry___Leaf_scorch'
    assert response_data['description'] == 'Leaf scorch is a fungal disease affecting strawberry leaves.'
    assert response_data['symptoms'] == 'Irregular, brown, and dead areas on leaves, often with a yellow halo.'
    assert response_data['causes'] == 'Caused by the fungus Diplocarpon earliana.'

def test_get_disease_info_not_found(client, token):
    response = client.get('/disease/disease_info/NonExistentDisease', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data is not None
    assert response_data.get('message') == 'Disease not found'

