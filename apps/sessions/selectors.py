"""
Database query functions for the sessions app.
All ORM queries live here, not in views or services.
"""
from django.db.models import QuerySet, Count, Q

from ..common.constants import SESSION_PUBLISHED, BOOKING_CONFIRMED
from .models import Session


def get_published_sessions(filters: dict = None) -> QuerySet:
    """Return all published sessions, optionally filtered, annotated with booking counts."""
    qs = Session.objects.filter(status=SESSION_PUBLISHED, is_deleted=False).select_related("creator")
    qs = qs.annotate(
        confirmed_bookings_count=Count(
            "bookings",
            filter=Q(bookings__status=BOOKING_CONFIRMED)
        )
    )
    if filters:
        if tag := filters.get("tag"):
            qs = qs.filter(tags__contains=[tag])
        if creator_id := filters.get("creator_id"):
            qs = qs.filter(creator_id=creator_id)
        if min_price := filters.get("min_price"):
            qs = qs.filter(price__gte=min_price)
        if max_price := filters.get("max_price"):
            qs = qs.filter(price__lte=max_price)
        if search := filters.get("search"):
            qs = qs.filter(title__icontains=search)
    return qs


def get_session_by_id(session_id: int) -> Session:
    """Return a single session by PK, or raise DoesNotExist."""
    return (
        Session.objects.filter(is_deleted=False)
        .select_related("creator")
        .annotate(
            confirmed_bookings_count=Count(
                "bookings",
                filter=Q(bookings__status=BOOKING_CONFIRMED)
            )
        )
        .get(pk=session_id)
    )


def get_creator_sessions(creator) -> QuerySet:
    """Return all sessions owned by a creator (any status) annotated with booking counts."""
    return (
        Session.objects.filter(creator=creator, is_deleted=False)
        .annotate(
            confirmed_bookings_count=Count(
                "bookings",
                filter=Q(bookings__status=BOOKING_CONFIRMED)
            )
        )
        .order_by("-created_at")
    )


def get_deleted_sessions(creator) -> QuerySet:
    """Return all soft-deleted sessions owned by a creator."""
    return Session.objects.filter(creator=creator, is_deleted=True).order_by("-created_at")


def get_all_sessions(creator) -> QuerySet:
    """Return all sessions owned by a creator including deleted ones."""
    return Session.objects.filter(creator=creator).order_by("-created_at")