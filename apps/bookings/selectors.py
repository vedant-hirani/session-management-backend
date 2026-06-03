"""
Database query functions for the bookings app.
"""
from django.db.models import QuerySet

from .models import Booking


def get_user_bookings(user, active_only: bool = False) -> QuerySet:
    """Return all bookings for a given user."""
    qs = Booking.objects.filter(user=user).select_related("session", "session__creator")
    if active_only:
        qs = qs.filter(status="confirmed")
    return qs


def get_booking_by_id(booking_id: int) -> Booking:
    """Return a single booking by PK."""
    return Booking.objects.select_related("session", "user").get(pk=booking_id)


def get_creator_bookings(creator) -> QuerySet:
    """
    Return all bookings for sessions owned by the creator.
    Used in the Creator Dashboard.
    """
    return (
        Booking.objects
        .filter(session__creator=creator)
        .select_related("session", "user")
        .order_by("-booked_at")
    )
