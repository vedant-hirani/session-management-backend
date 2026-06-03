"""
JWT helpers and custom token classes.
"""
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def generate_tokens(user):
    """Generate access + refresh tokens with custom claims."""
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["email"] = user.email
    refresh["name"] = user.get_full_name() or user.username
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def blacklist_refresh_token(refresh_token_str: str) -> bool:
    """
    Attempt to blacklist a refresh token.
    Returns True on success, False if token is invalid.
    """
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
        return True
    except TokenError:
        return False
