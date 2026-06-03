"""
Serializers for the sessions app.
"""
from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer
from .models import Session


class SessionListSerializer(serializers.ModelSerializer):
    """Compact serializer for catalog listing."""
    creator = UserPublicSerializer(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "title",
            "cover_image",
            "price",
            "duration_minutes",
            "scheduled_at",
            "status",
            "tags",
            "creator",
            "spots_remaining",
            "is_available",
        ]


class SessionDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer including description."""
    creator = UserPublicSerializer(read_only=True)
    spots_remaining = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

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
            "created_at",
            "updated_at",
        ]


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
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_max_attendees(self, value):
        if value < 1:
            raise serializers.ValidationError("Must allow at least 1 attendee.")
        return value
