"""
Views for the sessions app.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCreator
from .models import Session
from .selectors import get_published_sessions, get_session_by_id, get_creator_sessions
from .serializers import SessionListSerializer, SessionDetailSerializer, SessionWriteSerializer
from .services import create_session, update_session, cancel_session, delete_session
from .permissions import IsSessionCreatorOrReadOnly
from apps.common.pagination import StandardResultsPagination
from apps.common.constants import MSG_ONLY_CREATORS, MSG_SESSION_NOT_FOUND


class SessionCatalogView(APIView):
    """
    GET  /api/v1/sessions/        → public catalog of published sessions
    POST /api/v1/sessions/        → creator creates a new session
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        filters = {
            "search": request.query_params.get("search"),
            "tag": request.query_params.get("tag"),
            "min_price": request.query_params.get("min_price"),
            "max_price": request.query_params.get("max_price"),
            "creator_id": request.query_params.get("creator_id"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        sessions = get_published_sessions(filters)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(sessions, request)
        serializer = SessionListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_creator:
            return Response(
                {"detail": MSG_ONLY_CREATORS},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SessionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = create_session(request.user, serializer.validated_data)
        return Response(
            SessionDetailSerializer(session, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class SessionDetailView(APIView):
    """
    GET    /api/v1/sessions/<id>/   → session detail
    PATCH  /api/v1/sessions/<id>/   → creator updates session
    DELETE /api/v1/sessions/<id>/   → creator deletes session
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _get_session(self, pk):
        try:
            return get_session_by_id(pk)
        except Session.DoesNotExist:
            return None

    def get(self, request, pk):
        session = self._get_session(pk)
        if not session:
            return Response({"detail": MSG_SESSION_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        serializer = SessionDetailSerializer(session, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        session = self._get_session(pk)
        if not session:
            return Response({"detail": MSG_SESSION_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        serializer = SessionWriteSerializer(session, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = update_session(session, request.user, serializer.validated_data)
        return Response(SessionDetailSerializer(updated, context={"request": request}).data)

    def delete(self, request, pk):
        session = self._get_session(pk)
        if not session:
            return Response({"detail": MSG_SESSION_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        delete_session(session, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreatorSessionsView(APIView):
    """
    GET /api/v1/sessions/mine/  → list all sessions created by the logged-in creator
    """
    permission_classes = [IsAuthenticated, IsCreator]

    def get(self, request):
        sessions = get_creator_sessions(request.user)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(sessions, request)
        serializer = SessionListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CancelSessionView(APIView):
    """
    POST /api/v1/sessions/<id>/cancel/  → creator cancels their session
    """
    permission_classes = [IsAuthenticated, IsCreator]

    def post(self, request, pk):
        try:
            session = get_session_by_id(pk)
        except Session.DoesNotExist:
            return Response({"detail": MSG_SESSION_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        cancelled = cancel_session(session, request.user)
        return Response(SessionDetailSerializer(cancelled, context={"request": request}).data)
