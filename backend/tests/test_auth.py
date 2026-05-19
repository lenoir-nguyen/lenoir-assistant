"""
Tests for authentication endpoints (PIN verification and session tokens).

These tests verify that:
1. Login with correct passphrase + PIN returns a token
2. Login with wrong credentials is rejected with 401
3. Logout invalidates the token
4. Protected endpoints check for valid tokens
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
import secrets


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client for token storage."""
    return AsyncMock()


class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, client):
        """
        Test successful login with correct passphrase and PIN.

        When provided with:
        - Correct passphrase ("i am lenoir" or containing it)
        - Correct PIN (matching bcrypt hash from OWNER_PIN_HASH)

        Returns:
        - Status 200
        - { "token": "...", "is_owner": true }
        - Token stored in Redis with TTL
        """
        with patch("routers.auth.contains_passphrase") as mock_contains, \
             patch("routers.auth.verify_pin") as mock_verify_pin, \
             patch("routers.auth.redis_client.set") as mock_redis_set:

            mock_contains.return_value = True
            mock_verify_pin.return_value = True
            mock_redis_set.return_value = None

            response = client.post(
                "/auth/login",
                json={"passphrase": "i am lenoir", "pin": "1234"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert data["is_owner"] is True

            # Verify functions were called
            mock_contains.assert_called_once_with("i am lenoir")
            mock_verify_pin.assert_called_once_with("1234")

            # Verify token was stored in Redis
            mock_redis_set.assert_called_once()
            call_args = mock_redis_set.call_args
            assert "auth:" in call_args[0][0]

    def test_login_wrong_pin(self, client):
        """
        Test login with correct passphrase but wrong PIN.

        When provided with:
        - Correct passphrase
        - Wrong PIN (doesn't match bcrypt hash)

        Returns:
        - Status 401 Unauthorized
        """
        with patch("routers.auth.contains_passphrase") as mock_contains, \
             patch("routers.auth.verify_pin") as mock_verify_pin:

            mock_contains.return_value = True
            mock_verify_pin.return_value = False

            response = client.post(
                "/auth/login",
                json={"passphrase": "i am lenoir", "pin": "9999"}
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    def test_login_wrong_passphrase(self, client):
        """
        Test login with wrong passphrase.

        When provided with:
        - Wrong passphrase (doesn't contain "i am lenoir")
        - Any PIN

        Returns:
        - Status 401 Unauthorized
        """
        with patch("routers.auth.contains_passphrase") as mock_contains:

            mock_contains.return_value = False

            response = client.post(
                "/auth/login",
                json={"passphrase": "wrong passphrase", "pin": "1234"}
            )

            assert response.status_code == 401
            data = response.json()
            assert "detail" in data

    def test_login_missing_fields(self, client):
        """
        Test login with missing required fields.

        When passphrase or pin is missing:
        - Returns 422 Unprocessable Entity (validation error)
        """
        # Missing PIN
        response = client.post(
            "/auth/login",
            json={"passphrase": "i am lenoir"}
        )
        assert response.status_code == 422

        # Missing passphrase
        response = client.post(
            "/auth/login",
            json={"pin": "1234"}
        )
        assert response.status_code == 422

        # Empty request
        response = client.post("/auth/login", json={})
        assert response.status_code == 422


class TestLogoutEndpoint:
    """Tests for POST /auth/logout endpoint."""

    def test_logout_success(self, client):
        """
        Test successful logout with valid token.

        When provided with:
        - Valid Authorization header with Bearer token
        - Token exists in Redis

        Returns:
        - Status 200
        - { "message": "logged out" }
        - Token deleted from Redis
        """
        test_token = secrets.token_urlsafe(32)

        with patch("routers.auth.redis_client.get") as mock_redis_get, \
             patch("routers.auth.redis_client.delete") as mock_redis_delete:

            mock_redis_get.return_value = b'{"is_owner": true}'
            mock_redis_delete.return_value = None

            response = client.post(
                "/auth/logout",
                headers={"Authorization": f"Bearer {test_token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

            # Verify token was deleted
            mock_redis_delete.assert_called_once()

    def test_logout_invalid_token(self, client):
        """
        Test logout with invalid or expired token.

        When provided with:
        - Invalid Authorization header
        - Or token doesn't exist in Redis

        Returns:
        - Status 401 Unauthorized
        """
        with patch("routers.auth.redis_client.get") as mock_redis_get:

            mock_redis_get.return_value = None

            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer invalid-token"}
            )

            assert response.status_code == 401

    def test_logout_missing_auth_header(self, client):
        """
        Test logout without Authorization header.

        When Authorization header is missing:
        - Returns 403 Forbidden
        """
        response = client.post("/auth/logout")
        assert response.status_code == 403


class TestAuthIntegration:
    """Integration tests for auth workflow."""

    def test_login_then_chat_as_owner(self, client):
        """
        Test complete owner workflow: login → send message as owner.

        Simulates:
        1. Owner logs in with passphrase + PIN
        2. Gets a token
        3. Sends a chat message with token in Authorization header
        4. Backend uses owner system prompt
        """
        with patch("routers.auth.contains_passphrase") as mock_contains, \
             patch("routers.auth.verify_pin") as mock_verify_pin, \
             patch("routers.auth.redis_client.set") as mock_redis_set, \
             patch("routers.chat.redis_client.get") as mock_redis_get_chat, \
             patch("routers.chat.client.chat.completions.create") as mock_chat:

            # Step 1: Login
            mock_contains.return_value = True
            mock_verify_pin.return_value = True
            mock_redis_set.return_value = None

            login_response = client.post(
                "/auth/login",
                json={"passphrase": "i am lenoir", "pin": "1234"}
            )
            assert login_response.status_code == 200
            token = login_response.json()["token"]

            # Step 2: Chat as owner with token
            mock_redis_get_chat.return_value = b'{"is_owner": true}'
            mock_chat.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Owner response"))]
            )

            chat_response = client.post(
                "/chat/message",
                json={
                    "message": "Hello",
                    "language": "en",
                    "history": []
                },
                headers={"Authorization": f"Bearer {token}"}
            )

            assert chat_response.status_code == 200
            data = chat_response.json()
            assert "content" in data

    def test_guest_chat_without_token(self, client):
        """
        Test guest workflow: access chat without logging in.

        Simulates:
        1. Guest sends a chat message without Authorization header
        2. Backend uses guest system prompt
        3. Returns response
        """
        with patch("routers.chat.client.chat.completions.create") as mock_chat:

            mock_chat.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Guest response"))]
            )

            response = client.post(
                "/chat/message",
                json={
                    "message": "Hello",
                    "language": "en",
                    "history": []
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "content" in data
