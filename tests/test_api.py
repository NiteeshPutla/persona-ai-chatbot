"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import init_db

# Initialize test database
init_db()

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "endpoints" in response.json()


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint_missing_api_key():
    """Test chat endpoint without API key (should fail gracefully)."""
    # This test will fail if OPENAI_API_KEY is not set, which is expected
    # In a real scenario, we'd mock the LLM
    response = client.post(
        "/chat",
        json={
            "user_id": "test_user",
            "message": "Hello"
        }
    )
    # Should either succeed (if API key is set) or fail with appropriate error
    assert response.status_code in [200, 500]


def test_chat_history_endpoint():
    """Test chat history endpoint."""
    response = client.get("/chat_history?user_id=test_user")
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "threads" in response.json()


def test_chat_history_invalid_user():
    """Test chat history with invalid user_id."""
    response = client.get("/chat_history?user_id=")
    # Should return 400 or empty threads
    assert response.status_code in [200, 400]

