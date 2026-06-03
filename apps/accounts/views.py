"""
Views for authentication and user profile management.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from core.jwt import generate_tokens, blacklist_refresh_token
from .serializers import UserProfileSerializer, RoleSwitchSerializer, RegisterSerializer
from .services import update_user_profile, switch_user_role
from .permissions import IsSelfOrAdmin

User = get_user_model()


class OAuthCompleteView(APIView):
    """
    Called after social-auth completes OAuth.
    Issues JWT tokens and redirects the frontend with them as query params.
    This view is wired into the social auth pipeline via SOCIAL_AUTH_LOGIN_REDIRECT_URL.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = generate_tokens(request.user)
        frontend_url = settings.FRONTEND_URL
        redirect_url = (
            f"{frontend_url}/auth/callback"
            f"?access={tokens['access']}"
            f"&refresh={tokens['refresh']}"
        )
        return redirect(redirect_url)


class LogoutView(APIView):
    """Blacklist the refresh token to log out."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        success = blacklist_refresh_token(refresh_token)
        if not success:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    """Retrieve or update the authenticated user's own profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = update_user_profile(request.user, serializer.validated_data)
        return Response(UserProfileSerializer(user, context={"request": request}).data)


class RoleSwitchView(APIView):
    """Allow a user to switch their role between 'user' and 'creator'."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoleSwitchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = switch_user_role(request.user, serializer.validated_data["role"])
        # Re-issue tokens with updated role claim
        tokens = generate_tokens(user)
        return Response(
            {
                "detail": f"Role updated to {user.role}.",
                "role": user.role,
                **tokens,
            }
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({"status": "ok"})


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    Body: { "email": "...", "username": "...", "password": "...", "password2": "...", "role": "user"|"creator" }
    Returns: { "access": "...", "refresh": "...", "role": "...", "email": "...", "user_id": ... }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = generate_tokens(user)
        return Response(
            {
                **tokens,
                "role": user.role,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )
