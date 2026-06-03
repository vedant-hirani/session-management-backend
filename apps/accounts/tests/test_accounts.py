"""
Basic tests for the accounts app.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        role="user",
    )


@pytest.fixture
def creator(db):
    return User.objects.create_user(
        username="creator",
        email="creator@example.com",
        password="testpass123",
        role="creator",
    )


@pytest.mark.django_db
def test_health_check(api_client):
    response = api_client.get("/api/v1/auth/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_profile_requires_auth(api_client):
    response = api_client.get("/api/v1/auth/profile/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_profile_returns_user_data(api_client, user):
    from core.jwt import generate_tokens
    tokens = generate_tokens(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api_client.get("/api/v1/auth/profile/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_role_switch(api_client, user):
    from core.jwt import generate_tokens
    tokens = generate_tokens(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api_client.post("/api/v1/auth/profile/role/", {"role": "creator"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["role"] == "creator"
