import uuid
from django.conf import settings
from django.db import models


class DriverProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile"
    )

    license_number = models.CharField(
        max_length=50,
        unique=True
    )

    is_available = models.BooleanField(
        default=False
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver - {self.user}"

class DriverLocation(models.Model):
    driver = models.OneToOneField(
        "DriverProfile",
        on_delete=models.CASCADE,
        related_name="location"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    is_available = models.BooleanField(
        default=True
    )
    availability_status = models.CharField(
            max_length=10,
            choices=[
                ("ONLINE", "Online"),
                ("OFFLINE", "Offline"),
                ("BUSY", "Busy"),
            ],
            default="ONLINE",
    )

    def __str__(self):
        return f"{self.driver} - ({self.latitude}, {self.longitude})"
    
class VehicleType(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class Vehicle(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        related_name="vehicles"
    )

    vehicle_number = models.CharField(
        max_length=20,
        unique=True
    )

    model = models.CharField(
        max_length=100
    )

    color = models.CharField(
        max_length=50,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return self.vehicle_number

    class Meta:
        indexes = [
            models.Index(fields=["vehicle_type"]),
        ]
    
class RideStatus(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=30,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class Ride(models.Model):

    class RideType(models.TextChoices):
        NOW = "NOW", "Now"
        SCHEDULED = "SCHEDULED", "Scheduled"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="rides"
    )

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.PROTECT,
        related_name="rides",
        null=True,
        blank=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="rides",
        null=True,
        blank=True
    )

    status = models.ForeignKey(
        RideStatus,
        on_delete=models.PROTECT,
        related_name="rides"
    )

    pickup_address = models.CharField(
        max_length=255
    )

    drop_address = models.CharField(
        max_length=255
    )

    pickup_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    pickup_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    drop_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    drop_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    ride_type = models.CharField(
        max_length=20,
        choices=RideType.choices,
        default=RideType.NOW
    )

    fare = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id}"
    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["driver"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(fare__gte=0),
                name="ride_fare_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        ride_type="NOW",
                        scheduled_at__isnull=True
                    )
                    |
                    models.Q(
                        ride_type="SCHEDULED",
                        scheduled_at__isnull=False
                    )
                ),
                name="valid_ride_schedule",
            ),
        ]
