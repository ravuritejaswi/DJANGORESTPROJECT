from decimal import Decimal, InvalidOperation
from unicodedata import decimal
from uuid import UUID
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from .pagination import ServicePagination
from .models import Service
from .permissions import IsAdminOrProviderOwner
from .serializers import ServiceSerializer
from django.db.models import Q
from .models import Booking, Service
from .serializers import BookingSerializer, ServiceSerializer, PaymentInitiationSerializer
from .models import Booking, Payment
from .payment_gateway import MockPaymentGateway

from rest_framework.parsers import MultiPartParser, FormParser
from .models import ServiceImage
from .serializers import ServiceImageSerializer
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .serializers import PaymentWebhookSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """
    CRUD APIs and search APIs for services.
    """

    serializer_class = ServiceSerializer

    permission_classes = [
        IsAuthenticated,
        IsAdminOrProviderOwner,
    ]
    pagination_class = ServicePagination

    filter_backends = [
        OrderingFilter,
    ]

    ordering_fields = [
        "price",
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        queryset = Service.objects.select_related(
            "category",
            "provider",
            "provider__user",
            "provider__profile",
        ).all()

        # 1. Search by service name
        name = self.request.query_params.get("name")

        if name:
            queryset = queryset.filter(
                name__icontains=name.strip()
            )

        # 2. Search by category name or category UUID
        category = self.request.query_params.get("category")

        if category:
            category = category.strip()

            try:
                category_uuid = UUID(category)
                queryset = queryset.filter(
                    category_id=category_uuid
                )
            except ValueError:
                queryset = queryset.filter(
                    category__name__icontains=category
                )

        # 3. Search by provider name or provider UUID
        provider = self.request.query_params.get("provider")

        if provider:
            provider = provider.strip()

            try:
                provider_uuid = UUID(provider)
                queryset = queryset.filter(
                    provider_id=provider_uuid
                )
            except ValueError:
                queryset = queryset.filter(
                    provider__name__icontains=provider
                )

        # 4. Search by provider profile address
        location = self.request.query_params.get("location")

        if location:
            queryset = queryset.filter(
                provider__profile__address__icontains=location.strip()
            )

        # 5. Filter by minimum price
        min_price = self.request.query_params.get("min_price")

        if min_price:
            try:
                min_price_value = Decimal(min_price)
                queryset = queryset.filter(
                    price__gte=min_price_value
                )
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError({
                    "min_price": "Enter a valid minimum price."
                })

        # 6. Filter by maximum price
        max_price = self.request.query_params.get("max_price")

        if max_price:
            try:
                max_price_value = Decimal(max_price)
                queryset = queryset.filter(
                    price__lte=max_price_value
                )
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError({
                    "max_price": "Enter a valid maximum price."
                })

        # 7. Validate minimum and maximum price
        if min_price and max_price:
            if min_price_value > max_price_value:
                raise serializers.ValidationError({
                    "price": (
                        "Minimum price cannot be greater "
                        "than maximum price."
                    )
                })

        # 8. Filter by status
        status = self.request.query_params.get("status")

        if status:
            status = status.strip().upper()

            valid_statuses = [
                choice[0]
                for choice in Service.Status.choices
            ]

            if status not in valid_statuses:
                raise serializers.ValidationError({
                    "status": (
                        "Invalid status. Use ACTIVE or INACTIVE."
                    )
                })

            queryset = queryset.filter(
                status=status
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_staff:
            provider = serializer.validated_data.get("provider")

            if provider is None:
                raise serializers.ValidationError({
                    "provider": (
                        "Provider is required when an admin "
                        "creates a service."
                    )
                })

        else:
            try:
                provider = user.provider
            except user.provider.RelatedObjectDoesNotExist:
                raise serializers.ValidationError({
                    "provider": (
                        "The logged-in user is not registered "
                        "as a service provider."
                    )
                })

        serializer.save(provider=provider)

class BookingViewSet(viewsets.ModelViewSet):
    """
    API for creating and managing service bookings.
    """

    serializer_class = BookingSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user

        return Booking.objects.select_related(
            "customer",
            "provider",
            "provider__user",
            "service",
            "service__category",
        ).filter(
            Q(customer=user) | Q(provider__user=user)
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user

        provider = serializer.validated_data.get("provider")
        service = serializer.validated_data.get("service")

        if not provider.is_active:
            raise serializers.ValidationError({
                "provider": "This provider is not active."
            })

        if service.provider_id != provider.id:
            raise serializers.ValidationError({
                "service": (
                    "The selected service does not belong "
                    "to the selected provider."
                )
            })

        serializer.save(
            customer=user,
            status=Booking.Status.PENDING,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="cancel"
    )
    def cancel(self, request, pk=None):
        booking = self.get_object()

        # Only the customer or assigned provider
        # can cancel this booking.
        is_customer = booking.customer_id == request.user.id

        is_provider = (
            booking.provider.user_id == request.user.id
        )

        if not (is_customer or is_provider):
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to cancel this booking."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # A completed or already cancelled booking
        # cannot be cancelled again.
        if booking.status in [
            Booking.Status.COMPLETED,
            Booking.Status.CANCELLED,
        ]:
            return Response(
                {
                    "detail": (
                        "This booking cannot be cancelled "
                        "in its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )

class PaymentInitiationAPIView(APIView):
    """
    API for initiating a payment for a booking.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PaymentInitiationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        booking_id = serializer.validated_data["booking"]
        requested_amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data["payment_method"]

        # 1. Check whether the booking exists.
        booking = get_object_or_404(
            Booking,
            id=booking_id
        )

        # 2. Check whether the booking belongs to the user.
        if booking.customer_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You can initiate payment only "
                        "for your own booking."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Check whether the requested amount is correct.
        if requested_amount != booking.amount:
            return Response(
                {
                    "detail": (
                        "The payment amount does not "
                        "match the booking amount."
                    ),
                    "booking_amount": str(booking.amount),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Check whether the booking is payable.
        payable_statuses = [
            Booking.Status.PENDING,
            Booking.Status.CONFIRMED,
        ]

        if booking.status not in payable_statuses:
            return Response(
                {
                    "detail": (
                        "This booking is not payable "
                        "in its current status."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Prevent duplicate payments.
        if Payment.objects.filter(
            booking=booking
        ).exists():
            return Response(
                {
                    "detail": (
                        "A payment already exists "
                        "for this booking."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        # 6. Create the payment.
        with transaction.atomic():
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.amount,
                payment_method=payment_method,
                payment_status=Payment.Status.PENDING,
            )

        return Response(
            {
                "message": "Payment initiated successfully.",
                "payment_id": str(payment.id),
                "booking_id": str(payment.booking_id),
                "amount": str(payment.amount),
                "payment_status": payment.payment_status,
                "payment_method": payment.payment_method,
                "created_at": payment.created_at,
            },
            status=status.HTTP_201_CREATED
        )

class MockPaymentProcessAPIView(APIView):
    """
    Simulates payment processing using a mock gateway.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.select_related(
                "booking"
            ).get(
                id=payment_id
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Verify that the payment belongs
        # to the logged-in customer.
        if payment.booking.customer_id != request.user.id:
            return Response(
                {
                    "detail": (
                        "You do not have permission "
                        "to process this payment."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Prevent processing the same payment twice.
        if payment.payment_status != Payment.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending payments "
                        "can be processed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        mock_result = request.data.get(
            "result",
            "SUCCESS"
        )

        mock_result = str(mock_result).upper()

        if mock_result not in [
            "SUCCESS",
            "FAILED",
        ]:
            return Response(
                {
                    "detail": (
                        "Result must be SUCCESS "
                        "or FAILED."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if mock_result == "SUCCESS":
            gateway_result = (
                MockPaymentGateway.process_payment()
            )

            new_status = Payment.Status.SUCCESS

            transaction_id = (
                gateway_result["transaction_id"]
            )

        else:
            new_status = Payment.Status.FAILED

            transaction_id = (
                f"MOCK-FAILED-{payment.id.hex[:12].upper()}"
            )

        with transaction.atomic():
            payment.payment_status = new_status
            payment.transaction_id = transaction_id

            payment.save(
                update_fields=[
                    "payment_status",
                    "transaction_id",
                ]
            )

        return Response(
            {
                "message": "Payment processing completed.",
                "payment_id": str(payment.id),
                "booking_id": str(payment.booking_id),
                "amount": str(payment.amount),
                "payment_status": payment.payment_status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK
        )

class PaymentWebhookAPIView(APIView):
    """
    Handles payment confirmation events from
    the mock payment gateway.
    """

    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        serializer = PaymentWebhookSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        payment_id = serializer.validated_data[
            "payment_id"
        ]

        transaction_id = serializer.validated_data[
            "transaction_id"
        ]

        event_status = serializer.validated_data[
            "status"
        ]

        event_amount = serializer.validated_data[
            "amount"
        ]

        try:
            payment = Payment.objects.select_related(
                "booking"
            ).get(
                id=payment_id
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "detail": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate the payment amount.
        if event_amount != payment.amount:
            return Response(
                {
                    "detail": (
                        "The webhook amount does not "
                        "match the payment amount."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the transaction ID when
        # an existing transaction ID is present.
        if (
            payment.transaction_id
            and payment.transaction_id != transaction_id
        ):
            return Response(
                {
                    "detail": (
                        "The transaction ID does not "
                        "match the payment."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle repeated webhook events safely.
        if payment.payment_status == event_status:
            if payment.transaction_id == transaction_id:
                return Response(
                    {
                        "message": (
                            "This payment event was "
                            "already processed."
                        ),
                        "payment_status": (
                            payment.payment_status
                        ),
                    },
                    status=status.HTTP_200_OK
                )

        # Do not change a completed payment
        # to a different status.
        if payment.payment_status in [
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        ]:
            return Response(
                {
                    "detail": (
                        "This payment has already "
                        "been processed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking = payment.booking

        with transaction.atomic():
            payment.payment_status = event_status
            payment.transaction_id = transaction_id
            payment.save()

            if event_status == Payment.Status.SUCCESS:
                booking.status = Booking.Status.CONFIRMED
                booking.save()

        return Response(
            {
                "message": (
                    "Payment webhook processed successfully."
                ),
                "payment_id": str(payment.id),
                "booking_id": str(booking.id),
                "payment_status": payment.payment_status,
                "booking_status": booking.status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK
        )

class ServiceImageAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get(self, request, service_id):
        images = ServiceImage.objects.filter(
            service_id=service_id
        )

        serializer = ServiceImageSerializer(
            images,
            many=True,
            context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, service_id):
        service = get_object_or_404(
            Service,
            id=service_id
        )

        serializer = ServiceImageSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(service=service)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    def delete(self, request, service_id, image_id):
        image = get_object_or_404(
            ServiceImage,
            id=image_id,
            service_id=service_id
        )

        image.delete()

        return Response(
            {
                "message": "Service image deleted successfully."
            },
            status=status.HTTP_200_OK
        )