from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AdvancedRideFilterView, CancelledRidesView, CompletedRidesView, DailyRideCountView, DriverLocationView, DriverRideHistoryView, DriverViewSet, LargeDatasetRideView, NearbyDriverView, RideAggregationsView, RideViewSet, SlowRideQueryView, TotalCompletedRidesView, TotalFareEarnedView, UserActiveRidesView, VehicleViewSet

urlpatterns = [
    path(
        "rides/active/",
        UserActiveRidesView.as_view(),
        name="user-active-rides",
    ),
    path(
    "rides/total-completed/",
    TotalCompletedRidesView.as_view(),
    name="total-completed-rides",
    ),
    path(
    "rides/total-fare/",
    TotalFareEarnedView.as_view(),
    name="total-fare-earned",
    ),
    path(
    "rides/completed/",
    CompletedRidesView.as_view(),
    name="completed-rides",
    ),
    path(
    "rides/cancelled/",
    CancelledRidesView.as_view(),
    name="cancelled-rides",
    ),
    path(
    "rides/driver-history/",
    DriverRideHistoryView.as_view(),
    name="driver-ride-history",
    ),
    path(
    "rides/daily-count/",
    DailyRideCountView.as_view(),
    name="daily-ride-count",
    ),
    path(
    "rides/aggregations/",
    RideAggregationsView.as_view(),
    name="ride-aggregations",
    ),
    path(
    "slow-rides/",
    SlowRideQueryView.as_view(),
    name="slow-rides",
    ),
    path(
    "rides/filter/",
    AdvancedRideFilterView.as_view(),
    name="advanced-ride-filter"
    ),
    path(
    "rides/large-dataset/",
    LargeDatasetRideView.as_view(),
    name="large-dataset-rides"
    ),
    path(
    "drivers/location/",
    DriverLocationView.as_view(),
    name="driver-location",
    ),
    path(
    "drivers/nearby/",
    NearbyDriverView.as_view(),
    name="nearby-drivers",
    ),
]

router = DefaultRouter()
router.register("drivers", DriverViewSet, basename="drivers")
router.register("vehicles", VehicleViewSet, basename="vehicles")
router.register("rides", RideViewSet, basename="rides")

urlpatterns += router.urls