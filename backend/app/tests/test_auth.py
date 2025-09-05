"""
Authentication tests.

Tests for authentication endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate

client = TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "confirm_password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "agree_to_terms": True
    }


@pytest.fixture
def test_login_data():
    """Test login data fixture."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123"
    }


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_user_success(self, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == test_user_data["email"]
        assert data["user"]["first_name"] == test_user_data["first_name"]
        assert data["user"]["last_name"] == test_user_data["last_name"]
    
    def test_register_user_duplicate_email(self, test_user_data):
        """Test registration with duplicate email."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_password_mismatch(self, test_user_data):
        """Test registration with password mismatch."""
        test_user_data["confirm_password"] = "DifferentPassword123"
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422
        assert "Passwords do not match" in str(response.json())
    
    def test_register_user_weak_password(self, test_user_data):
        """Test registration with weak password."""
        test_user_data["password"] = "weak"
        test_user_data["confirm_password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422
        assert "Password must be at least 8 characters long" in str(response.json())
    
    def test_register_user_terms_not_agreed(self, test_user_data):
        """Test registration without agreeing to terms."""
        test_user_data["agree_to_terms"] = False
        
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422
        assert "You must agree to the terms and conditions" in str(response.json())
    
    def test_login_success(self, test_user_data, test_login_data):
        """Test successful user login."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post("/api/v1/auth/login", json=test_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "tokens" in data
        assert data["user"]["email"] == test_login_data["email"]
    
    def test_login_invalid_credentials(self, test_login_data):
        """Test login with invalid credentials."""
        response = client.post("/api/v1/auth/login", json=test_login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_authorized(self, test_user_data, test_login_data):
        """Test getting current user with authentication."""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post("/api/v1/auth/login", json=test_login_data)
        
        # Get access token
        access_token = login_response.json()["tokens"]["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test basic health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
    
    def test_readiness_check(self):
        """Test readiness check."""
        response = client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "services" in data
    
    def test_liveness_check(self):
        """Test liveness check."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
