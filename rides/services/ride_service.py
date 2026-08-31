from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.tasks import send_ride_completion_notification
from rides.models import DriverProfile, Ride, RideStatus
from rides.services.notification_service import notify_ride_completion


def get_status(status_name):
    return RideStatus.objects.get(name=status_name)


@transaction.atomic
def accept_ride(ride_id, user):

    ride = Ride.objects.select_for_update().get(pk=ride_id)

    driver = DriverProfile.objects.filter(user=user).first()

    if not driver:
        raise PermissionDenied("You are not registered as a driver.")

    if not driver.is_available:
        raise ValidationError("Driver is not available.")

    requested_status = get_status("REQUESTED")
    accepted_status = get_status("ACCEPTED")

    if ride.status_id != requested_status.id:
        raise ValidationError("Ride is not available for acceptance.")

    # Ride must not already have a driver
    if ride.driver_id is not None:
        raise ValidationError("Ride has already been assigned to a driver.")

    # Driver must not have another active ride
    conflicting_statuses = RideStatus.objects.filter(
        name__in=[
            "ACCEPTED",
            "DRIVER_ARRIVING",
            "STARTED",
        ]
    )

    if Ride.objects.filter(driver=driver, status__in=conflicting_statuses).exists():
        raise ValidationError("Driver already has a conflicting ride.")

    # Assign driver and accept ride
    ride.driver = driver
    ride.status = accepted_status

    ride.save(
        update_fields=[
            "driver",
            "status",
            "updated_at",
        ]
    )

    return ride


def cancel_ride(ride_id):
    ride = Ride.objects.get(pk=ride_id)

    cancelled_status = get_status("CANCELLED")

    if ride.status.name in ["COMPLETED", "CANCELLED"]:
        raise ValidationError("Ride cannot be cancelled in its current status.")

    ride.status = cancelled_status

    if ride.driver:
        ride.driver.is_available = True
        ride.driver.save(update_fields=["is_available"])

    ride.save(update_fields=["status", "updated_at"])

    return ride


def create_ride(user, validated_data):
    requested_status = get_status("REQUESTED")

    return Ride.objects.create(
        user=user,
        status=requested_status,
        driver=validated_data.get("driver"),
        vehicle=validated_data.get("vehicle"),
        **{
            key: value
            for key, value in validated_data.items()
            if key not in ["driver", "vehicle"]
        }
    )


@transaction.atomic
def start_ride(ride_id):
    ride = Ride.objects.select_for_update().get(pk=ride_id)

    accepted_status = get_status("ACCEPTED")
    started_status = get_status("STARTED")

    if ride.status_id != accepted_status.id:
        raise ValidationError("Ride cannot be started in its current status.")

    ride.status = started_status

    ride.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return ride


@transaction.atomic
def complete_ride(ride_id):
    ride = Ride.objects.select_for_update().get(pk=ride_id)

    started_status = get_status("STARTED")
    completed_status = get_status("COMPLETED")

    if ride.status_id != started_status.id:
        raise ValidationError("Ride cannot be completed in its current status.")

    ride.status = completed_status

    ride.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    notify_ride_completion(ride)

    return ride
