"""
Global reusable DRF permission classes.
"""
from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsCreator(BasePermission):
    """Allow access only to users with the Creator role."""

    message = "You must be a Creator to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CREATOR
        )


class IsRegularUser(BasePermission):
    """Allow access only to users with the User role."""

    message = "This action is restricted to regular users."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.USER
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission: only the owner of an object may edit it.
    Assumes the model instance has an `owner` or `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        from rest_framework.permissions import SAFE_METHODS
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "user", None)
        return owner == request.user
