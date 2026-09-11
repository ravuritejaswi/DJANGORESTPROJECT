"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from common.health import (
    HealthCheckView,
    DatabaseHealthCheckView,
    RedisHealthCheckView,
)

from accounts.views import (
    NotificationListAPIView,
    NotificationReadAllAPIView,
    NotificationReadAPIView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Ride Booking API",
        default_version="v1",
        description=(
            "API documentation for the Ride Booking Backend. "
            "This API provides user authentication, profiles, "
            "driver management, vehicle management, ride booking, "
            "ride status management, notifications, and driver location services."
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("rides.urls")),
    path("api/v1/", include("rides.urls")),
    path("api/notifications/", NotificationListAPIView.as_view(), name="notifications"),
    path(
    "api/health/",
    HealthCheckView.as_view(),
    name="health",
    ),

    path(
    "api/health/database/",
    DatabaseHealthCheckView.as_view(),
    name="health-database",
    ),

    path(
    "api/health/redis/",
    RedisHealthCheckView.as_view(),
    name="health-redis",
    ),
    path(
        "api/notifications/<int:pk>/read/",
        NotificationReadAPIView.as_view(),
        name="notification-read",
    ),
    path(
        "api/notifications/read-all/",
        NotificationReadAllAPIView.as_view(),
        name="notification-read-all",
    ),
    path(
        "api/v1/notifications/",
        NotificationListAPIView.as_view(),
        name="v1-notifications",
    ),
    path(
        "api/v1/notifications/<int:pk>/read/",
        NotificationReadAPIView.as_view(),
        name="v1-notification-read",
    ),
    path(
        "api/v1/notifications/read-all/",
        NotificationReadAllAPIView.as_view(),
        name="v1-notification-read-all",
    ),
    path("accounts/", include("accounts.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("silk/", include("silk.urls", namespace="silk")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
