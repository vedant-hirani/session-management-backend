"""
Business logic for the sessions app.
"""
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..common.constants import (
    SESSION_CANCELLED,
    BOOKING_CANCELLED,
    MSG_ONLY_CREATORS,
    MSG_OWN_SESSIONS_ONLY,
    MSG_OWN_CANCEL_ONLY,
    MSG_OWN_DELETE_ONLY,
    MSG_OWN_RESTORE_ONLY,
    MSG_CANNOT_UPDATE_DELETED,
    MSG_CANNOT_UPDATE_CANCELLED,
    MSG_CANNOT_CANCEL_DELETED,
    MSG_SESSION_ALREADY_CANCELLED,
    MSG_SESSION_ALREADY_DELETED,
    MSG_SESSION_NOT_DELETED,
)
from .models import Session


def create_session(creator, data: dict) -> Session:
    """Create a new session owned by the given creator."""
    if not creator.is_creator:
        raise PermissionDenied(MSG_ONLY_CREATORS)
    session = Session.objects.create(creator=creator, **data)
    return session


def update_session(session: Session, creator, data: dict) -> Session:
    """Update a session. Only the owner can update it."""
    if session.creator != creator:
        raise PermissionDenied(MSG_OWN_SESSIONS_ONLY)
    if session.is_deleted:
        raise ValidationError(MSG_CANNOT_UPDATE_DELETED)
    if session.status == SESSION_CANCELLED:
        raise ValidationError(MSG_CANNOT_UPDATE_CANCELLED)
    for field, value in data.items():
        setattr(session, field, value)
    session.save()
    return session


def cancel_session(session: Session, creator) -> Session:
    """Cancel a session. Only the owner can cancel it."""
    if session.creator != creator:
        raise PermissionDenied(MSG_OWN_CANCEL_ONLY)
    if session.is_deleted:
        raise ValidationError(MSG_CANNOT_CANCEL_DELETED)
    if session.status == SESSION_CANCELLED:
        raise ValidationError(MSG_SESSION_ALREADY_CANCELLED)
    session.status = SESSION_CANCELLED
    session.save(update_fields=["status"])
    # Cancel and refund all confirmed bookings
    _refund_confirmed_bookings(session)
    return session


def delete_session(session: Session, creator) -> None:
    """Soft delete a session. Only the owner can delete it."""
    if session.creator != creator:
        raise PermissionDenied(MSG_OWN_DELETE_ONLY)
    if session.is_deleted:
        raise ValidationError(MSG_SESSION_ALREADY_DELETED)

    # If session is not already cancelled, cancel it first and refund bookings
    if session.status != SESSION_CANCELLED:
        session.status = SESSION_CANCELLED
        _refund_confirmed_bookings(session)

    # Now soft delete the session
    session.is_deleted = True
    session.save(update_fields=["is_deleted", "status"])


def restore_session(session: Session, creator) -> Session:
    """Restore a soft-deleted session. Only the owner can restore it."""
    if session.creator != creator:
        raise PermissionDenied(MSG_OWN_RESTORE_ONLY)
    if not session.is_deleted:
        raise ValidationError(MSG_SESSION_NOT_DELETED)
    session.is_deleted = False
    session.save(update_fields=["is_deleted"])
    return session


def _refund_confirmed_bookings(session: Session) -> None:
    """Cancel all confirmed bookings for a session and refund users."""
    from decimal import Decimal
    from ..common.constants import BOOKING_CONFIRMED

    confirmed_bookings = session.bookings.filter(status=BOOKING_CONFIRMED)
    for booking in confirmed_bookings:
        booking.status = BOOKING_CANCELLED
        booking.save(update_fields=["status"])
        price = Decimal(str(session.price))
        balance = Decimal(str(booking.user.wallet_balance))
        booking.user.wallet_balance = balance + price
        booking.user.save(update_fields=["wallet_balance"])