"""
Booking-specific DRF permissions.
"""
from rest_framework.permissions import BasePermission


class IsBookingOwner(BasePermission):
    """Allow access only to the user who made the booking."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
