import pytest
from app import create_app, db
from app.models import Prediction, Image
from app.config import TestingConfig
from flask_jwt_extended import create_access_token
from io import BytesIO
from datetime import datetime

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Add some sample data
        image = Image(image_path='/path/to/image.jpg')
        db.session.add(image)
        db.session.commit()

        prediction1 = Prediction(
            user_id=1,
            image_id=image.id,
            predicted_class='Tomato Leaf Spot',
            confidence_percentage=85.0,
            prediction_date=datetime(2024, 7, 15, 14, 30, 0)
        )
        prediction2 = Prediction(
            user_id=1,
            image_id=image.id,
            predicted_class='Tomato Early Blight',
            confidence_percentage=75.0,
            prediction_date=datetime(2024, 7, 16, 10, 0, 0)
        )
        db.session.add(prediction1)
        db.session.add(prediction2)
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

def test_view_prediction_history_success(client, token):
    response = client.get('/history/view_prediction_history?start_date=2024-07-15&end_date=2024-07-17', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response_data = response.get_json()

    # Sort the response data by prediction_date
    response_data.sort(key=lambda x: x['prediction_date'])

    # Debugging: Print the response data and length
    print(f"Response Data: {response_data}")
    print(f"Number of Records Returned: {len(response_data)}")

    assert len(response_data) == 2
    assert response_data[0]['predicted_class'] == 'Tomato Leaf Spot'
    assert response_data[1]['predicted_class'] == 'Tomato Early Blight'

def test_download_prediction_history_pdf_success(client, token):
    response = client.get('/history/download_prediction_history_pdf?start_date=2024-07-15&end_date=2024-07-17', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert response.headers['Content-Disposition'] == 'attachment; filename=prediction_history.pdf'
    assert isinstance(BytesIO(response.data), BytesIO)  # Corrected to check if response.data is a BytesIO object

def test_view_prediction_history_no_records(client, token):
    response = client.get('/history/view_prediction_history?start_date=2024-07-01&end_date=2024-07-10', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data == []

def test_download_prediction_history_pdf_no_records(client, token):
    response = client.get('/history/download_prediction_history_pdf?start_date=2024-07-01&end_date=2024-07-10', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert response.headers['Content-Disposition'] == 'attachment; filename=prediction_history.pdf'
    assert isinstance(BytesIO(response.data), BytesIO)  # Corrected to check if response.data is a BytesIO object
