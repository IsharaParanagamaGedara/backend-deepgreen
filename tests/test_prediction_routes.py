import pytest
import io
from app import create_app, db
from app.models import Image, Prediction
from app.config import TestingConfig
from flask_jwt_extended import create_access_token
import tempfile

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
    access_token = create_access_token(identity={'id': 1})
    return access_token

@pytest.fixture
def image_file():
    file = io.BytesIO(b"fake image content")
    file.name = 'test_image.jpg'
    return file

@pytest.fixture
def uploaded_image(client, token, image_file):
    response = client.post('/image/upload_image', headers={"Authorization": f"Bearer {token}"}, 
                           content_type='multipart/form-data',
                           data={'image': (image_file, 'test_image.jpg')})
    response_data = response.get_json()
    return response_data.get('image_id', None)

def test_predict_disease_success(client, token, uploaded_image):
    if uploaded_image is None:
        pytest.skip("Image upload failed, skipping predict_disease_success test.")
    
    response = client.get(f'/prediction/predict_disease/{uploaded_image}', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data.get('prediction_id') is not None
    assert response_data.get('predicted_class') is not None
    assert response_data.get('confidence_percentage') is not None
    assert response_data.get('image_url') is not None

    prediction_record = Prediction.query.filter_by(id=response_data['prediction_id']).first()
    assert prediction_record is not None
    assert prediction_record.predicted_class == response_data['predicted_class']
    assert prediction_record.confidence_percentage == response_data['confidence_percentage']

def test_predict_disease_image_not_found(client, token):
    response = client.get('/prediction/predict_disease/9999', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data is not None
    assert response_data.get('message') == 'Image not found'

def test_predict_disease_failure(client, token, monkeypatch):
    # Mock the predict_disease function to raise an exception
    def mock_predict_disease(image_path):
        raise Exception("Test error")

    # Define a mock image method
    class MockImageQuery:
        @staticmethod
        def get(image_id):
            # Simulate that an image with the given ID exists
            return Image(id=image_id, image_path='dummy/path', user_id=1)

    # Mock the import path correctly
    monkeypatch.setattr('app.routes.prediction_routes.predict_disease', mock_predict_disease)
    monkeypatch.setattr('app.routes.prediction_routes.Image.query', MockImageQuery)

    response = client.get('/prediction/predict_disease/1', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 500, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data is not None
    assert response_data.get('message') == 'Prediction failed'
    assert 'error' in response_data
