"""
Session-specific DRF permissions.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSessionCreatorOrReadOnly(BasePermission):
    """
    Object-level: only the creator of a session may modify it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.creator == request.user
