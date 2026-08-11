from rest_framework import serializers
from .models import DriverProfile, Vehicle, VehicleType

class VehicleNestedSerializer(serializers.ModelSerializer):
    vehicle_type = serializers.CharField(source="vehicle_type.name", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "vehicle_type",
            "vehicle_number",
        ]
class DriverProfileSerializer(serializers.ModelSerializer):
    vehicles = VehicleNestedSerializer(many=True, read_only=True)
    class Meta:
        model = DriverProfile
        fields = [
            "id",
            "user",
            "license_number",
            "is_available",
            "rating",
            "vehicles",
        ]
        read_only_fields = ["id", "rating"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "driver",
            "vehicle_type",
            "vehicle_number",
            "model",
            "color",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "driver",
            "vehicle_type",
            "vehicle_number",
            "model",
            "color",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_vehicle_number(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Vehicle registration number is required."
            )

        if Vehicle.objects.filter(vehicle_number=value).exists():
            raise serializers.ValidationError(
                "Vehicle with this vehicle number already exists."
            )

        return value

    def validate_driver(self, value):
        if not DriverProfile.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Invalid driver ID."
            )

        return value

    def validate_vehicle_type(self, value):
        if not VehicleType.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Invalid vehicle type."
            )

        return value
    def validate(self, attrs):
        request = self.context.get("request")
        driver = attrs.get("driver")

        if request and request.user:
            if driver.user != request.user:
                raise serializers.ValidationError({
                    "driver": "You can only manage your own vehicle."
                })

        return attrs
