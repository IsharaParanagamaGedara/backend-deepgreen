import pytest
import io
import os
from app import create_app, db
from app.models import Image
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

def test_upload_image_success(client, token, image_file):
    response = client.post('/image/upload_image', headers={"Authorization": f"Bearer {token}"}, 
                           content_type='multipart/form-data',
                           data={'image': (image_file, 'test_image.jpg')})
    assert response.status_code == 201, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data['message'] == 'Image uploaded successfully'
    assert 'image_id' in response_data
    assert 'file_path' in response_data

    image_record = Image.query.filter_by(id=response_data['image_id']).first()
    assert image_record is not None
    assert os.path.isfile(image_record.image_path)

def test_upload_image_no_file(client, token):
    response = client.post('/image/upload_image', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400, f"Response: {response.data}"
    assert response.get_json()['message'] == 'No image file provided'

def test_upload_image_no_selected_file(client, token):
    response = client.post('/image/upload_image', headers={"Authorization": f"Bearer {token}"}, 
                           content_type='multipart/form-data',
                           data={'image': (io.BytesIO(b''), '')})
    assert response.status_code == 400, f"Response: {response.data}"
    assert response.get_json()['message'] == 'No selected file'

def test_upload_image_failure(client, token, monkeypatch):
    def mock_save_image(file):
        raise Exception("Test error")

    monkeypatch.setattr('app.routes.image_routes.save_image', mock_save_image)

    response = client.post('/image/upload_image', headers={"Authorization": f"Bearer {token}"}, 
                           content_type='multipart/form-data',
                           data={'image': (io.BytesIO(b"fake image content"), 'test_image.jpg')})
    assert response.status_code == 500, f"Response: {response.data}"
    assert response.get_json()['message'] == 'Image upload failed'
    assert 'error' in response.get_json()
