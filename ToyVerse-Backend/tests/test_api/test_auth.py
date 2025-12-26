import pytest

class TestAuthAPI:
    def test_register(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "password123",
                "role": "customer"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["role"] == "customer"

    def test_login_success(self, client, customer_user):
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testcustomer",
                "password": "customer123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "testcustomer"

    def test_login_invalid_credentials(self, client, customer_user):
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testcustomer",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

    def test_get_current_user(self, client, customer_token):
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testcustomer"
        assert "permissions" in data

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401
