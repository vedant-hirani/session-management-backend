"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def root_health_check(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Sessions Marketplace API is running."
    })

urlpatterns = [
    path("", root_health_check, name="root-health-check"),
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/sessions/", include("apps.sessions.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),

    # Social auth (OAuth callbacks handled here, JWT issued after)
    path("social/", include("social_django.urls", namespace="social")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

