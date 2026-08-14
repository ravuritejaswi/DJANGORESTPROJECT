from django.http import request
from rest_framework import serializers
from .models import (DriverProfile, Vehicle, VehicleType, Ride, RideStatus)

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

    # For PATCH, driver may not be included in the request.
    # Use the existing vehicle driver in that case.
        if driver is None and self.instance is not None:
            driver = self.instance.driver

        if request and request.user.is_authenticated and driver:
            if driver.user != request.user:
                raise serializers.ValidationError({
                    "driver": "You can only manage your own vehicle."
                })

        return attrs

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = [
            "id",
            "user",
            "driver",
            "vehicle",
            "status",
            "pickup_address",
            "drop_address",
            "pickup_latitude",
            "pickup_longitude",
            "drop_latitude",
            "drop_longitude",
            "ride_type",
            "fare",
            "scheduled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")

    # 1. User must be authenticated
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError({
                "user": "User must be authenticated."
            })

        pickup_address = attrs.get("pickup_address")
        drop_address = attrs.get("drop_address")
        ride_type = attrs.get("ride_type")

    # 2. Pickup location must exist
        if not pickup_address or not pickup_address.strip():
            raise serializers.ValidationError({
                "pickup_address": "Pickup location is required."
            })

    # 3. Drop location must exist
        if not drop_address or not drop_address.strip():
            raise serializers.ValidationError({
                "drop_address": "Drop location is required."
            })

    # 4. Pickup and drop must be different
        if pickup_address.strip().lower() == drop_address.strip().lower():
            raise serializers.ValidationError({
                "drop_address": "Pickup and drop locations must be different."
            })

    # 5. Check for conflicting active ride
        active_statuses = [
            "REQUESTED",
            "ACCEPTED",
            "DRIVER_ARRIVING",
            "STARTED",
        ]

        has_active_ride = Ride.objects.filter(
            user=request.user,
            status__name__in=active_statuses
        ).exists()

        if has_active_ride:
            raise serializers.ValidationError({
                "user": "You already have an active ride."
            })

    # 6. Validate ride type
        if ride_type not in [
            Ride.RideType.NOW,
            Ride.RideType.SCHEDULED,
        ]:
            raise serializers.ValidationError({
                "ride_type": "Invalid ride type."
            })

    # 7. NOW ride cannot have scheduled time
        scheduled_at = attrs.get("scheduled_at")

        if ride_type == Ride.RideType.NOW and scheduled_at is not None:
            raise serializers.ValidationError({
                "scheduled_at": "NOW rides cannot have a scheduled time."
            })

    # 8. SCHEDULED ride must have scheduled time
        if ride_type == Ride.RideType.SCHEDULED and scheduled_at is None:
            raise serializers.ValidationError({
                "scheduled_at": "Scheduled rides must have a scheduled time."
            })

        return attrs

class RideStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ["status"]

    def validate_status(self, new_status):
        ride = self.instance

        if not ride:
            return new_status

        current_status = ride.status.name
        next_status = new_status.name

        allowed_transitions = {
            "REQUESTED": ["ACCEPTED"],
            "ACCEPTED": ["STARTED"],
            "STARTED": ["COMPLETED"],
            "COMPLETED": [],
            "CANCELLED": [],
        }

        if next_status not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Invalid status transition: "
                f"{current_status} → {next_status}"
            )

        return new_status
