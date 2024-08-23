import pytest
from app.models import User
from itsdangerous import URLSafeTimedSerializer

@pytest.fixture
def user():
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "Test1234!"
    }

def test_register(client, user):
    response = client.post('/auth/register', json=user)
    assert response.status_code == 201
    assert response.get_json()['message'] == "User registered successfully"

    # Check if the user is actually created in the database
    db_user = User.query.filter_by(email=user['email']).first()
    assert db_user is not None
    assert db_user.email == user['email']

def test_register_missing_data(client):
    response = client.post('/auth/register', json={"email": "test@example.com"})
    assert response.status_code == 400
    assert "Missing data" in response.get_json()['error']

def test_register_existing_email(client, user):
    client.post('/auth/register', json=user)
    response = client.post('/auth/register', json=user)
    assert response.status_code == 400
    assert "Email already registered" in response.get_json()['error']

def test_register_invalid_password(client):
    user = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "short"
    }
    response = client.post('/auth/register', json=user)
    assert response.status_code == 400
    assert "Password must be at least 8 characters long" in response.get_json()['error']

def test_login(client, user):
    client.post('/auth/register', json=user)
    response = client.post('/auth/login', json={"email": user['email'], "password": user['password']})
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_login_invalid_credentials(client, user):
    client.post('/auth/register', json=user)
    response = client.post('/auth/login', json={"email": user['email'], "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.get_json()['message']

def test_logout(client, user):
    client.post('/auth/register', json=user)
    login_response = client.post('/auth/login', json={"email": user['email'], "password": user['password']})
    token = login_response.get_json()['token']
    
    response = client.post('/auth/logout', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Successfully logged out" in response.get_json()['message']

def test_forgot_password(client, user, mocker):
    client.post('/auth/register', json=user)
    
    mock_send = mocker.patch('flask_mail.Mail.send', return_value=True)
    response = client.post('/auth/forgot-password', json={"email": user['email']})
    assert response.status_code == 200
    assert "Password reset email sent" in response.get_json()['message']
    assert mock_send.called

def test_forgot_password_email_not_found(client):
    response = client.post('/auth/forgot-password', json={"email": "nonexistent@example.com"})
    assert response.status_code == 404
    assert "Email not found" in response.get_json()['error']

def test_reset_password(client, user, mocker):
    client.post('/auth/register', json=user)
    
    # Generate a token
    with client.application.app_context():
        s = URLSafeTimedSerializer(client.application.config['SECRET_KEY'])
        token = s.dumps(user['email'], salt='email-confirm')
    
    new_password = "NewPassword123!"
    response = client.post(f'/auth/reset-password/{token}', json={"password": new_password})
    assert response.status_code == 200
    assert "Password has been reset" in response.get_json()['message']

    # Verify the password was updated
    login_response = client.post('/auth/login', json={"email": user['email'], "password": new_password})
    assert login_response.status_code == 200
    assert "token" in login_response.get_json()

def test_reset_password_invalid_token(client):
    response = client.post('/auth/reset-password/invalid_token', json={"password": "NewPassword123!"})
    assert response.status_code == 400
    assert "Invalid or expired token" in response.get_json()['error']
