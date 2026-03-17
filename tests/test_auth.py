import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root path"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_register_user():
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


def test_login():
    """Test user login"""
    # Register user first
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": "testuser2",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_protected_route_without_token():
    """Test unauthorized access to protected route"""
    response = client.get("/items/")
    assert response.status_code == 401


def test_protected_route_with_token():
    """Test accessing protected route with token"""
    # Register and login user
    user_data = {
        "username": "testuser3",
        "email": "test3@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "testuser3",
        "password": "testpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Access protected route with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/items/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "user" in data


def test_refresh_token():
    """Test refresh token"""
    # Register and login user
    user_data = {
        "username": "testuser4",
        "email": "test4@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "testuser4",
        "password": "testpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    response_data = login_response.json()
    refresh_token = response_data["refresh_token"]
    
    # Use refresh token to get new access token
    refresh_data = {"refresh_token": refresh_token}
    refresh_response = client.post("/auth/refresh", json=refresh_data)
    assert refresh_response.status_code == 200
    token_data = refresh_response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_logout():
    """Test user logout"""
    # Register and login user
    user_data = {
        "username": "testuser5",
        "email": "test5@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "testuser5",
        "password": "testpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    response_data = login_response.json()
    refresh_token = response_data["refresh_token"]
    
    # Logout
    logout_data = {"refresh_token": refresh_token}
    logout_response = client.post("/auth/logout", json=logout_data)
    assert logout_response.status_code == 200
    
    # Try to use logged out refresh token
    refresh_response = client.post("/auth/refresh", json=logout_data)
    assert refresh_response.status_code == 401


def test_invalid_refresh_token():
    """Test invalid refresh token"""
    invalid_token = "invalid_refresh_token"
    refresh_data = {"refresh_token": invalid_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 401