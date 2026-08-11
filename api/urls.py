from django.urls import path
from .views import hello
from rides.views import DriverViewSet
from .views import VehicleListCreateView, VehicleDetailView

urlpatterns = [
    path("", hello),

    path("drivers/", DriverViewSet.as_view({
        "get": "list",
        "post": "create",
    })),

    path("drivers/<uuid:pk>/", DriverViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
    })),
    path("vehicles/", VehicleListCreateView.as_view()),
    path("vehicles/<uuid:pk>/", VehicleDetailView.as_view()),
]
