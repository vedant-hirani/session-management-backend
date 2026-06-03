"""
URL patterns for the accounts app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import OAuthCompleteView, LogoutView, ProfileView, health_check, RegisterView
from .token_view import ObtainTokenView

urlpatterns = [
    # Health
    path("health/", health_check, name="health-check"),

    # JWT — login with username+password
    path("token/", ObtainTokenView.as_view(), name="token-obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Register new user (role is chosen here and fixed permanently)
    path("register/", RegisterView.as_view(), name="register"),

    # OAuth callback → issues JWT and redirects frontend
    path("oauth/complete/", OAuthCompleteView.as_view(), name="oauth-complete"),

    # Session management
    path("logout/", LogoutView.as_view(), name="logout"),

    # Profile (role is read-only — cannot be changed post-registration)
    path("profile/", ProfileView.as_view(), name="profile"),
]
