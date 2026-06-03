"""
URL patterns for the bookings app.
"""
from django.urls import path

from .views import (
    UserBookingsView,
    BookingDetailView,
    CancelBookingView,
    CreatorBookingOverviewView,
)

urlpatterns = [
    path("", UserBookingsView.as_view(), name="user-bookings"),
    path("creator/", CreatorBookingOverviewView.as_view(), name="creator-bookings"),
    path("<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("<int:pk>/cancel/", CancelBookingView.as_view(), name="booking-cancel"),
]
