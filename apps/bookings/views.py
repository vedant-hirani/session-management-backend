"""
Views for the bookings app.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsCreator
from ..sessions.models import Session
from .models import Booking
from .selectors import get_user_bookings, get_booking_by_id, get_creator_bookings
from .serializers import BookingSerializer
from .services import create_booking, cancel_booking
from ..common.pagination import StandardResultsPagination
from ..common.constants import (
    MSG_SESSION_ID_REQUIRED,
    MSG_SESSION_NOT_FOUND,
    MSG_BOOKING_NOT_FOUND,
    MSG_NOT_AUTHORIZED,
)


class UserBookingsView(APIView):
    """
    GET  /api/v1/bookings/         → list current user's bookings
    POST /api/v1/bookings/         → book a session
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_only = request.query_params.get("active") == "true"
        bookings = get_user_bookings(request.user, active_only=active_only)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        session_id = request.data.get("session_id")
        if not session_id:
            return Response(
                {"detail": MSG_SESSION_ID_REQUIRED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            return Response({"detail": MSG_SESSION_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        booking = create_booking(request.user, session)
        return Response(
            BookingSerializer(booking, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    """
    GET    /api/v1/bookings/<id>/        → booking detail
    DELETE /api/v1/bookings/<id>/cancel/ → cancel a booking
    """
    permission_classes = [IsAuthenticated]

    def _get_booking(self, pk, user):
        try:
            booking = get_booking_by_id(pk)
        except Booking.DoesNotExist:
            return None, Response({"detail": MSG_BOOKING_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        if booking.user != user:
            return None, Response({"detail": MSG_NOT_AUTHORIZED}, status=status.HTTP_403_FORBIDDEN)
        return booking, None

    def get(self, request, pk):
        booking, error = self._get_booking(pk, request.user)
        if error:
            return error
        return Response(BookingSerializer(booking, context={"request": request}).data)


class CancelBookingView(APIView):
    """
    POST /api/v1/bookings/<id>/cancel/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = get_booking_by_id(pk)
        except Booking.DoesNotExist:
            return Response({"detail": MSG_BOOKING_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        cancelled = cancel_booking(booking, request.user)
        return Response(BookingSerializer(cancelled, context={"request": request}).data)


class CreatorBookingOverviewView(APIView):
    """
    GET /api/v1/bookings/creator/  → Creator sees all bookings on their sessions
    """
    permission_classes = [IsAuthenticated, IsCreator]

    def get(self, request):
        bookings = get_creator_bookings(request.user)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
