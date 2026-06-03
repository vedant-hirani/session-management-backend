"""
Database query functions for the sessions app.
All ORM queries live here, not in views or services.
"""
from django.db.models import QuerySet

from apps.common.constants import SESSION_PUBLISHED
from .models import Session


def get_published_sessions(filters: dict = None) -> QuerySet:
    """Return all published sessions, optionally filtered."""
    qs = Session.objects.filter(status=SESSION_PUBLISHED).select_related("creator")
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
    return Session.objects.select_related("creator").get(pk=session_id)


def get_creator_sessions(creator) -> QuerySet:
    """Return all sessions owned by a creator (any status)."""
    return Session.objects.filter(creator=creator).order_by("-created_at")
