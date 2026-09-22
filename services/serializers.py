from rest_framework import serializers
from .models import Booking
from .models import Category, Provider, Service


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    provider_name = serializers.CharField(
        source="provider.name",
        read_only=True
    )

    provider = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(),
        required=False,
    )

    class Meta:
        model = Service

        fields = [
            "id",
            "name",
            "description",
            "price",
            "status",
            "category",
            "category_name",
            "provider",
            "provider_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "provider_name",
            "category_name",
            "created_at",
            "updated_at",
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Price cannot be negative."
            )

        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Service name cannot be empty."
            )

        return value.strip()

class BookingSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.email",
        read_only=True
    )

    provider_name = serializers.CharField(
        source="provider.name",
        read_only=True
    )

    service_name = serializers.CharField(
        source="service.name",
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer",
            "customer_name",
            "provider",
            "provider_name",
            "service",
            "service_name",
            "booking_date",
            "booking_time",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "customer_name",
            "provider_name",
            "service_name",
            "created_at",
            "updated_at",
        ]