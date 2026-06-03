"""
Business logic for the bookings app.
"""
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import transaction

from ..common.constants import (
    BOOKING_CONFIRMED,
    BOOKING_CANCELLED,
    SESSION_PUBLISHED,
    SESSION_CANCELLED,
    MSG_SESSION_UNAVAILABLE,
    MSG_SESSION_FULLY_BOOKED,
    MSG_ALREADY_BOOKED,
    MSG_OWN_BOOKINGS_ONLY,
    MSG_BOOKING_ALREADY_CANCELLED,
    MSG_CANNOT_CANCEL_DELETED_SESSION,
)
from ..sessions.models import Session
from .models import Booking


@transaction.atomic
def create_booking(user, session: Session) -> Booking:
    """
    Book a session for a user.
    Validates:
    - Session must be published and not deleted
    - Spots must be available
    - User must not have an active (confirmed) booking for this session
      (cancelled bookings are ignored — user can re-book after cancelling)
    Uses select_for_update to avoid race conditions.
    """
    # Fetch locked session
    locked_session = Session.objects.select_for_update().get(pk=session.pk)

    if locked_session.is_deleted or locked_session.status != SESSION_PUBLISHED:
        raise ValidationError(MSG_SESSION_UNAVAILABLE)

    if locked_session.spots_remaining <= 0:
        raise ValidationError(MSG_SESSION_FULLY_BOOKED)

    # Only block if there's already a confirmed booking — cancelled ones are fine
    if Booking.objects.filter(user=user, session=locked_session, status=BOOKING_CONFIRMED).exists():
        raise ValidationError(MSG_ALREADY_BOOKED)

    # If a cancelled booking exists, reuse it instead of creating a duplicate
    existing = Booking.objects.filter(user=user, session=locked_session).first()
    if existing:
        existing.status = BOOKING_CONFIRMED
        existing.save(update_fields=["status"])
        return existing

    booking = Booking.objects.create(
        user=user,
        session=locked_session,
        status=BOOKING_CONFIRMED,
    )
    return booking


@transaction.atomic
def cancel_booking(booking: Booking, user) -> Booking:
    """
    Cancel a booking. Only the booking owner can cancel it.
    """
    if booking.user != user:
        raise PermissionDenied(MSG_OWN_BOOKINGS_ONLY)

    if booking.status == BOOKING_CANCELLED:
        raise ValidationError(MSG_BOOKING_ALREADY_CANCELLED)
    
    # Check if session is already cancelled or deleted
    if booking.session.status == SESSION_CANCELLED or booking.session.is_deleted:
        raise ValidationError(MSG_CANNOT_CANCEL_DELETED_SESSION)

    booking.status = BOOKING_CANCELLED
    booking.save(update_fields=["status"])
    
    # Refund the amount to user's wallet
    from decimal import Decimal
    price = Decimal(str(booking.session.price))
    balance = Decimal(str(booking.user.wallet_balance))
    booking.user.wallet_balance = balance + price
    booking.user.save(update_fields=["wallet_balance"])

    return booking
