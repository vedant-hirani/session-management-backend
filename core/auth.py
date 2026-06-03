"""
Global OAuth pipeline helpers and JWT issuance utilities.
"""
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect as django_redirect
from rest_framework_simplejwt.tokens import RefreshToken

from core.jwt import generate_tokens


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


def issue_jwt_and_redirect(backend, user, is_new=False, *args, **kwargs):
    """
    Final social-auth pipeline step.
    Issues JWT tokens and redirects directly to the frontend callback URL
    with tokens as query parameters.

    By returning an HttpResponseRedirect the pipeline short-circuits and
    the response is sent straight to the browser — no session cookie or
    secondary authenticated redirect is needed.

    This eliminates the AuthStateMissing / session-cookie issues because
    the JWT is issued within the *same* request that already validated
    the OAuth state.
    """
    if not user:
        return None

    tokens = generate_tokens(user)
    params = {
        "access": tokens["access"],
        "refresh": tokens["refresh"],
    }
    if is_new:
        params["needs_setup"] = "1"

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    redirect_url = f"{frontend_url}/auth/callback?{urlencode(params)}"
    return django_redirect(redirect_url)
