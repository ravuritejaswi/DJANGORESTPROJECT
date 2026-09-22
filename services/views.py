from decimal import Decimal, InvalidOperation
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
from .serializers import BookingSerializer, ServiceSerializer


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