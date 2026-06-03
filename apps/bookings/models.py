"""
Booking model — records a user booking a session.
"""
from django.db import models
from django.conf import settings

from ..common.constants import BOOKING_STATUS_CHOICES, BOOKING_CONFIRMED


class Booking(models.Model):
    """
    A booking made by a User for a Session.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    session = models.ForeignKey(
        "marketplace_sessions.Session",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default=BOOKING_CONFIRMED,
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optionally store payment reference
    payment_reference = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-booked_at"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        # Prevent double-booking same session by same user
        unique_together = [["user", "session"]]

    def __str__(self):
        return f"{self.user.email} → {self.session.title} [{self.status}]"

    @property
    def is_active(self):
        return self.status == BOOKING_CONFIRMED
