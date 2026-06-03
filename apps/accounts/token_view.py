"""
Simple username+password → JWT login endpoint.
Used for testing (OAuth is the primary auth method).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from core.jwt import generate_tokens

User = get_user_model()


class ObtainTokenView(APIView):
    """
    POST /api/v1/auth/token/
    Body: { "username": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "...", "role": "...", "email": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Support login by email or username
        if "@" in username:
            # passed as email directly — use as-is for authenticate
            user = authenticate(request, username=username, password=password)
        else:
            # passed as username — look up the email first
            try:
                user_obj = User.objects.get(username=username)
                user = authenticate(request, username=user_obj.email, password=password)
            except User.DoesNotExist:
                user = None
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = generate_tokens(user)
        return Response({
            **tokens,
            "role": user.role,
            "email": user.email,
            "user_id": user.id,
        })
