"""
Business logic for the bookings app.
"""
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.common.constants import BOOKING_CONFIRMED, BOOKING_CANCELLED, SESSION_PUBLISHED
from apps.sessions.models import Session
from .models import Booking


def create_booking(user, session: Session) -> Booking:
    """
    Book a session for a user.
    Validates:
    - Session must be published
    - Spots must be available
    - User must not have already booked the same session
    """
    if session.status != SESSION_PUBLISHED:
        raise ValidationError("This session is not available for booking.")

    if session.spots_remaining <= 0:
        raise ValidationError("This session is fully booked.")

    if Booking.objects.filter(user=user, session=session).exists():
        raise ValidationError("You have already booked this session.")

    booking = Booking.objects.create(
        user=user,
        session=session,
        status=BOOKING_CONFIRMED,
    )
    return booking


def cancel_booking(booking: Booking, user) -> Booking:
    """
    Cancel a booking. Only the booking owner can cancel it.
    """
    if booking.user != user:
        raise PermissionDenied("You can only cancel your own bookings.")

    if booking.status == BOOKING_CANCELLED:
        raise ValidationError("Booking is already cancelled.")
    
    # Check if session is already cancelled or deleted
    from apps.common.constants import SESSION_CANCELLED
    if booking.session.status == SESSION_CANCELLED or booking.session.is_deleted:
        raise ValidationError("Cannot cancel booking for a cancelled or deleted session.")

    booking.status = BOOKING_CANCELLED
    booking.save(update_fields=["status"])
    
    # Refund the amount to user's wallet
    from decimal import Decimal
    price = Decimal(str(booking.session.price))
    balance = Decimal(str(booking.user.wallet_balance))
    booking.user.wallet_balance = balance + price
    booking.user.save(update_fields=["wallet_balance"])

    return booking
