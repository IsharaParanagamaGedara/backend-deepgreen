import pytest
from app import create_app, db
from app.models import CureSuggestion, PlantDisease
from app.config import TestingConfig
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Create a sample disease and suggestions for testing
        disease = PlantDisease(disease_name="Test Disease")
        db.session.add(disease)
        db.session.commit()
        
        suggestions = [
            CureSuggestion(disease_id=disease.id, suggestion="Test Suggestion 1"),
            CureSuggestion(disease_id=disease.id, suggestion="Test Suggestion 2")
        ]
        db.session.add_all(suggestions)
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

def test_detailed_cure_suggestions_success(client, token):
    response = client.get('/suggestion/detailed_cure_suggestions', 
                          headers={"Authorization": f"Bearer {token}"}, 
                          query_string={'disease_name': 'Test Disease'})
    assert response.status_code == 200, f"Response: {response.data}"
    response_data = response.get_json()
    
    assert len(response_data) == 2
    assert any(s['suggestion'] == 'Test Suggestion 1' for s in response_data)
    assert any(s['suggestion'] == 'Test Suggestion 2' for s in response_data)

def test_detailed_cure_suggestions_disease_not_found(client, token):
    response = client.get('/suggestion/detailed_cure_suggestions', 
                          headers={"Authorization": f"Bearer {token}"}, 
                          query_string={'disease_name': 'Nonexistent Disease'})
    assert response.status_code == 404, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data['message'] == 'Disease not found'

def test_detailed_cure_suggestions_no_disease_name(client, token):
    response = client.get('/suggestion/detailed_cure_suggestions', 
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data['message'] == 'Disease name is required'

def test_detailed_cure_suggestions_no_suggestions(client, token):
    # Remove the existing suggestions
    CureSuggestion.query.delete()
    db.session.commit()
    
    response = client.get('/suggestion/detailed_cure_suggestions', 
                          headers={"Authorization": f"Bearer {token}"}, 
                          query_string={'disease_name': 'Test Disease'})
    assert response.status_code == 404, f"Response: {response.data}"
    response_data = response.get_json()
    assert response_data['message'] == 'No cure suggestions found for this disease'
