"""
Tests for the sessions app.
"""
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.sessions.models import Session

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def creator(db):
    return User.objects.create_user(
        username="creator",
        email="creator@example.com",
        password="pass",
        role="creator",
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="pass",
        role="user",
    )


@pytest.fixture
def session_obj(db, creator):
    return Session.objects.create(
        title="Test Session",
        description="A test session",
        creator=creator,
        price="10.00",
        duration_minutes=60,
        max_attendees=5,
        scheduled_at=timezone.now() + timezone.timedelta(days=1),
        status="published",
    )


@pytest.mark.django_db
def test_catalog_is_public(api_client, session_obj):
    response = api_client.get("/api/v1/sessions/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["pagination"]["count"] == 1


@pytest.mark.django_db
def test_session_detail_public(api_client, session_obj):
    response = api_client.get(f"/api/v1/sessions/{session_obj.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Test Session"


@pytest.mark.django_db
def test_create_session_requires_creator_role(api_client, regular_user):
    from core.jwt import generate_tokens
    tokens = generate_tokens(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    payload = {
        "title": "New Session",
        "description": "desc",
        "price": "0.00",
        "duration_minutes": 30,
        "max_attendees": 1,
        "scheduled_at": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "status": "published",
    }
    response = api_client.post("/api/v1/sessions/", payload, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_creator_can_create_session(api_client, creator):
    from core.jwt import generate_tokens
    tokens = generate_tokens(creator)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    payload = {
        "title": "Creator Session",
        "description": "desc",
        "price": "25.00",
        "duration_minutes": 45,
        "max_attendees": 3,
        "scheduled_at": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "status": "published",
    }
    response = api_client.post("/api/v1/sessions/", payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Creator Session"
