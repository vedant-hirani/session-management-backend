"""
Serializers for the sessions app.
"""
from rest_framework import serializers

from ..accounts.serializers import UserPublicSerializer
from .models import Session


class SessionListSerializer(serializers.ModelSerializer):
    """Compact serializer for catalog listing."""
    creator = UserPublicSerializer(read_only=True)
    spots_remaining = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "title",
            "cover_image",
            "price",
            "duration_minutes",
            "max_attendees",
            "scheduled_at",
            "status",
            "tags",
            "creator",
            "spots_remaining",
            "is_available",
            "is_featured",
            "rating",
            "booking_count",
            "category",
        ]

    def get_spots_remaining(self, obj):
        confirmed_count = getattr(obj, "confirmed_bookings_count", None)
        if confirmed_count is None:
            from ..common.constants import BOOKING_CONFIRMED
            confirmed_count = obj.bookings.filter(status=BOOKING_CONFIRMED).count()
        return max(0, obj.max_attendees - confirmed_count)


class SessionDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer including description."""
    creator = UserPublicSerializer(read_only=True)
    spots_remaining = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(read_only=True)
    already_booked = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            "id",
            "title",
            "description",
            "cover_image",
            "price",
            "duration_minutes",
            "max_attendees",
            "scheduled_at",
            "status",
            "tags",
            "creator",
            "spots_remaining",
            "is_available",
            "already_booked",
            "created_at",
            "updated_at",
            "is_featured",
            "rating",
            "booking_count",
            "category",
        ]

    def get_spots_remaining(self, obj):
        confirmed_count = getattr(obj, "confirmed_bookings_count", None)
        if confirmed_count is None:
            from ..common.constants import BOOKING_CONFIRMED
            confirmed_count = obj.bookings.filter(status=BOOKING_CONFIRMED).count()
        return max(0, obj.max_attendees - confirmed_count)

    def get_already_booked(self, obj):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            from ..bookings.models import Booking
            from ..common.constants import BOOKING_CONFIRMED
            return Booking.objects.filter(
                user=request.user, session=obj, status=BOOKING_CONFIRMED
            ).exists()
        return False


class SessionWriteSerializer(serializers.ModelSerializer):
    """Used by Creators to create/update sessions."""

    class Meta:
        model = Session
        fields = [
            "title",
            "description",
            "cover_image",
            "price",
            "duration_minutes",
            "max_attendees",
            "scheduled_at",
            "status",
            "tags",
            "category",
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_max_attendees(self, value):
        if value < 1:
            raise serializers.ValidationError("Must allow at least 1 attendee.")
        return value
