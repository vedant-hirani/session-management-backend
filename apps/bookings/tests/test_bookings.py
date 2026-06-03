"""
Tests for the bookings app.
"""
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.sessions.models import Session
from apps.bookings.models import Booking

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def creator(db):
    return User.objects.create_user(
        username="creator", email="creator@example.com", password="pass", role="creator"
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="user", email="user@example.com", password="pass", role="user"
    )


@pytest.fixture
def session_obj(db, creator):
    return Session.objects.create(
        title="Bookable Session",
        description="desc",
        creator=creator,
        price="0.00",
        duration_minutes=60,
        max_attendees=5,
        scheduled_at=timezone.now() + timezone.timedelta(days=1),
        status="published",
    )


@pytest.mark.django_db
def test_user_can_book_session(api_client, regular_user, session_obj):
    from core.jwt import generate_tokens
    tokens = generate_tokens(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api_client.post("/api/v1/bookings/", {"session_id": session_obj.pk})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "confirmed"


@pytest.mark.django_db
def test_cannot_double_book(api_client, regular_user, session_obj):
    from core.jwt import generate_tokens
    tokens = generate_tokens(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    api_client.post("/api/v1/bookings/", {"session_id": session_obj.pk})
    response = api_client.post("/api/v1/bookings/", {"session_id": session_obj.pk})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_cancel_booking(api_client, regular_user, session_obj):
    from core.jwt import generate_tokens
    booking = Booking.objects.create(user=regular_user, session=session_obj, status="confirmed")
    tokens = generate_tokens(regular_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = api_client.post(f"/api/v1/bookings/{booking.pk}/cancel/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "cancelled"
