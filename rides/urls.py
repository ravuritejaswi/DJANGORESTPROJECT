from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, RideViewSet

router = DefaultRouter()

router.register("drivers", DriverViewSet, basename="drivers")
router.register("rides", RideViewSet, basename="rides")

urlpatterns = router.urls