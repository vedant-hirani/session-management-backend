"""
Account-specific DRF permissions.
"""
from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """
    Allow users to access/modify only their own profile.
    Admins (is_staff) can access any profile.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
