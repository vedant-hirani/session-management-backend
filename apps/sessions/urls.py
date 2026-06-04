"""
URL patterns for the sessions app.
"""
from django.urls import path

from .views import (
    SessionCatalogView,
    SessionDetailView,
    CreatorSessionsView,
    CancelSessionView,
    FileUploadView,
)

urlpatterns = [
    path("", SessionCatalogView.as_view(), name="session-catalog"),
    path("mine/", CreatorSessionsView.as_view(), name="creator-sessions"),
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    path("<int:pk>/", SessionDetailView.as_view(), name="session-detail"),
    path("<int:pk>/cancel/", CancelSessionView.as_view(), name="session-cancel"),
]

