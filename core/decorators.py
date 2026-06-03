"""
Utility decorators for views and services.
"""
import functools
import logging

from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def handle_service_exceptions(func):
    """
    Decorator for service layer functions called from views.
    Catches unexpected exceptions and returns a standardised 500 response.
    Use on view methods, not pure service functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.exception("Unhandled exception in %s: %s", func.__name__, exc)
            return Response(
                {"detail": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return wrapper


def require_role(*roles):
    """
    View decorator that enforces role-based access.
    Usage:
        @require_role('creator')
        def my_view(request, ...): ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.role not in roles:
                return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
