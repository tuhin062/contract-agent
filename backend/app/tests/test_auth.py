"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """Tests for authentication endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers, test_user):
        """Test get current user endpoint."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
    
    def test_get_current_user_no_auth(self, client: TestClient):
        """Test get current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No auth header
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test get current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401
    
    def test_logout(self, client: TestClient, auth_headers):
        """Test logout endpoint."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
    
    def test_register_by_admin(self, client: TestClient, admin_headers):
        """Test user registration by admin."""
        response = client.post(
            "/api/v1/auth/register",
            headers=admin_headers,
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "newuserpassword123",
                "role": "regular"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
    
    def test_register_by_non_admin(self, client: TestClient, auth_headers):
        """Test user registration by non-admin fails."""
        response = client.post(
            "/api/v1/auth/register",
            headers=auth_headers,
            json={
                "email": "anotheruser@example.com",
                "name": "Another User",
                "password": "password123",
                "role": "regular"
            }
        )
        assert response.status_code == 403
    
    def test_token_refresh(self, client: TestClient, test_user):
        """Test token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
