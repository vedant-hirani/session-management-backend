"""
Serializers for the bookings app.
"""
from rest_framework import serializers

from ..sessions.serializers import SessionListSerializer
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """Full booking detail including nested session info."""
    session = SessionListSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source="session",
        queryset=__import__("apps.sessions.models", fromlist=["Session"]).Session.objects.all(),
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "session",
            "session_id",
            "status",
            "booked_at",
            "updated_at",
            "payment_reference",
        ]
        read_only_fields = ["id", "status", "booked_at", "updated_at", "payment_reference"]
