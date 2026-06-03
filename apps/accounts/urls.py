"""
URL patterns for the accounts app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    OAuthCompleteView, OAuthSetupView,
    LogoutView, ProfileView,
    health_check, RegisterView,
)
from .token_view import ObtainTokenView

urlpatterns = [
    # Health
    path("health/", health_check, name="health-check"),

    # JWT — login with username+password
    path("token/", ObtainTokenView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Register new user (role chosen here, fixed permanently)
    path("register/", RegisterView.as_view(), name="register"),

    # OAuth: Django social-auth redirects here after Google/GitHub auth
    path("oauth/complete/", OAuthCompleteView.as_view(), name="oauth-complete"),

    # OAuth: brand-new users set username + role here
    path("oauth/setup/", OAuthSetupView.as_view(), name="oauth-setup"),

    # Session management
    path("logout/", LogoutView.as_view(), name="logout"),

    # Profile (role is read-only post-registration)
    path("profile/", ProfileView.as_view(), name="profile"),
]
