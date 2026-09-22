from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, ServiceViewSet


router = DefaultRouter()

router.register(
    r"services",
    ServiceViewSet,
    basename="service"
)

router.register(
    r"bookings",
    BookingViewSet,
    basename="booking"
)

urlpatterns = router.urls