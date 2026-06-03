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
    if session.is_deleted:
        raise ValidationError("Cannot update a deleted session.")
    if session.status == SESSION_CANCELLED:
        raise ValidationError("Cannot update a cancelled session.")
    for field, value in data.items():
        setattr(session, field, value)
    session.save()
    return session


def cancel_session(session: Session, creator) -> Session:
    """Cancel a session. Only the owner can cancel it."""
    if session.creator != creator:
        raise PermissionDenied("You can only cancel your own sessions.")
    if session.is_deleted:
        raise ValidationError("Cannot cancel a deleted session.")
    if session.status == SESSION_CANCELLED:
        raise ValidationError("Session is already cancelled.")
    session.status = SESSION_CANCELLED
    session.save(update_fields=["status"])
    # Cancel and refund all confirmed bookings
    from decimal import Decimal
    from apps.common.constants import BOOKING_CANCELLED
    
    confirmed_bookings = session.bookings.filter(status="confirmed")
    for booking in confirmed_bookings:
        booking.status = BOOKING_CANCELLED
        booking.save(update_fields=["status"])
        # Refund the amount to user's wallet
        price = session.price
        balance = Decimal(str(booking.user.wallet_balance))
        booking.user.wallet_balance = balance + price
        booking.user.save(update_fields=["wallet_balance"])
    return session


def delete_session(session: Session, creator) -> None:
    """Soft delete a session. Only the owner can delete it."""
    if session.creator != creator:
        raise PermissionDenied("You can only delete your own sessions.")
    if session.is_deleted:
        raise ValidationError("Session is already deleted.")
    
    from apps.common.constants import SESSION_CANCELLED, BOOKING_CANCELLED
    from decimal import Decimal
    
    # If session is not already cancelled, cancel it first and refund bookings
    if session.status != SESSION_CANCELLED:
        session.status = SESSION_CANCELLED
        # Cancel and refund all confirmed bookings
        confirmed_bookings = session.bookings.filter(status="confirmed")
        for booking in confirmed_bookings:
            booking.status = BOOKING_CANCELLED
            booking.save(update_fields=["status"])
            # Refund the amount to user's wallet
            price = session.price
            balance = Decimal(str(booking.user.wallet_balance))
            booking.user.wallet_balance = balance + price
            booking.user.save(update_fields=["wallet_balance"])
    
    # Now soft delete the session
    session.is_deleted = True
    session.save(update_fields=["is_deleted", "status"])


def restore_session(session: Session, creator) -> Session:
    """Restore a soft-deleted session. Only the owner can restore it."""
    if session.creator != creator:
        raise PermissionDenied("You can only restore your own sessions.")
    if not session.is_deleted:
        raise ValidationError("Session is not deleted.")
    session.is_deleted = False
    session.save(update_fields=["is_deleted"])
    return session