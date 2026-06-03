"""
Global OAuth pipeline helpers and JWT issuance utilities.
"""
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """Return a dict with access and refresh JWT tokens for a given user."""
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    refresh["email"] = user.email
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def save_avatar_from_oauth(backend, user, response, *args, **kwargs):
    """
    Social Auth pipeline step.
    Saves the OAuth provider's avatar URL to the user profile if not already set.
    """
    avatar_url = None

    if backend.name == "google-oauth2":
        avatar_url = response.get("picture")
    elif backend.name == "github":
        avatar_url = response.get("avatar_url")

    if avatar_url and not user.avatar:
        user.avatar = avatar_url
        user.save(update_fields=["avatar"])
