from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BookingViewSet,
    PaymentInitiationAPIView,
    MockPaymentProcessAPIView,
    PaymentWebhookAPIView,
    ServiceViewSet,
)


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


urlpatterns = router.urls + [
    path(
        "payments/initiate/",
        PaymentInitiationAPIView.as_view(),
        name="payment-initiate",
    ),
    path(
        "payments/<uuid:payment_id>/process/",
        MockPaymentProcessAPIView.as_view(),
        name="payment-process",
    ),
    path(
    "payments/webhook/",
    PaymentWebhookAPIView.as_view(),
    name="payment-webhook",
    ),
]
