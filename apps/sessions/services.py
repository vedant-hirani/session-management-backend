"""
Business logic for the sessions app.
"""
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.common.constants import SESSION_CANCELLED
from .models import Session


def create_session(creator, data: dict) -> Session:
    """Create a new session owned by the given creator."""
    if not creator.is_creator:
        raise PermissionDenied("Only creators can create sessions.")
    session = Session.objects.create(creator=creator, **data)
    return session


def update_session(session: Session, creator, data: dict) -> Session:
    """Update a session. Only the owner can update it."""
    if session.creator != creator:
        raise PermissionDenied("You can only edit your own sessions.")
    for field, value in data.items():
        setattr(session, field, value)
    session.save()
    return session


def cancel_session(session: Session, creator) -> Session:
    """Cancel a session. Only the owner can cancel it."""
    if session.creator != creator:
        raise PermissionDenied("You can only cancel your own sessions.")
    if session.status == SESSION_CANCELLED:
        raise ValidationError("Session is already cancelled.")
    session.status = SESSION_CANCELLED
    session.save(update_fields=["status"])
    # TODO: notify all confirmed bookings
    return session


def delete_session(session: Session, creator) -> None:
    """Hard delete a session. Only the owner and only if no confirmed bookings exist."""
    if session.creator != creator:
        raise PermissionDenied("You can only delete your own sessions.")
    if session.bookings.filter(status="confirmed").exists():
        raise ValidationError(
            "Cannot delete a session with confirmed bookings. Cancel it instead."
        )
    session.delete()
