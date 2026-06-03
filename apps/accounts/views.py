"""
Views for authentication and user profile management.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.jwt import generate_tokens, blacklist_refresh_token
from .serializers import UserProfileSerializer, RegisterSerializer, OAuthSetupSerializer
from .services import update_user_profile
from .permissions import IsSelfOrAdmin

User = get_user_model()


class OAuthCompleteView(APIView):
    """
    GET /api/v1/auth/oauth/complete/
    Fallback endpoint after social-auth completes OAuth.
    The primary flow uses the pipeline step (issue_jwt_and_redirect) which
    redirects directly to the frontend. This view is kept as a safety net.
    - Issues JWT tokens
    - If the user is brand-new (needs role setup), redirects with ?needs_setup=1
    - Otherwise redirects straight to the dashboard
    """
    # Accept session auth (set by social_django after OAuth) AND JWT
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tokens = generate_tokens(request.user)
        frontend_url = settings.FRONTEND_URL

        # Check if the social-auth pipeline flagged this as a new user
        is_new = request.session.pop("oauth_new_user", False)

        redirect_url = (
            f"{frontend_url}/auth/callback"
            f"?access={tokens['access']}"
            f"&refresh={tokens['refresh']}"
        )
        if is_new:
            redirect_url += "&needs_setup=1"

        return redirect(redirect_url)


class OAuthSetupView(APIView):
    """
    POST /api/v1/auth/oauth/setup/
    Called after Google OAuth for brand-new users.
    Lets them set their username and choose their role (user | creator).
    Body: { "username": "...", "role": "user"|"creator" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OAuthSetupSerializer(
            request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Re-issue tokens so role is baked into the new JWT
        tokens = generate_tokens(user)
        return Response(
            {
                **tokens,
                "role": user.role,
                "email": user.email,
                "user_id": user.id,
            }
        )


from apps.common.constants import MSG_REFRESH_TOKEN_REQUIRED, MSG_INVALID_TOKEN, MSG_LOGGED_OUT


class LogoutView(APIView):
    """Blacklist the refresh token to log out."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": MSG_REFRESH_TOKEN_REQUIRED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        success = blacklist_refresh_token(refresh_token)
        if not success:
            return Response(
                {"detail": MSG_INVALID_TOKEN},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": MSG_LOGGED_OUT}, status=status.HTTP_200_OK)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({"status": "ok"})


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    Body: { "email": "...", "username": "...", "password": "...", "password2": "...", "role": "user"|"creator" }
    Role is chosen at registration and is permanently fixed — it cannot be changed afterwards.
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
