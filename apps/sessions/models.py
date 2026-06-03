"""
Session model — a bookable session created by a Creator.
"""
from django.db import models
from django.conf import settings

from apps.common.constants import SESSION_STATUS_CHOICES, SESSION_PUBLISHED, BOOKING_CONFIRMED


class Session(models.Model):
    """
    A session offered by a Creator.
    Users can browse and book published sessions.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_sessions",
    )
    cover_image = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duration_minutes = models.PositiveIntegerField(default=60)
    max_attendees = models.PositiveIntegerField(default=1)
    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default=SESSION_PUBLISHED,
    )
    tags = models.JSONField(default=list, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f"{self.title} by {self.creator.email}"

    @property
    def spots_remaining(self):
        confirmed = self.bookings.filter(status=BOOKING_CONFIRMED).count()
        return max(0, self.max_attendees - confirmed)

    @property
    def is_available(self):
        return self.status == SESSION_PUBLISHED and self.spots_remaining > 0
