from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from rides.models import DriverProfile, Ride, RideStatus

def get_status(status_name):
    return RideStatus.objects.get(name=status_name)
@transaction.atomic
def accept_ride(ride_id, user):

    ride = Ride.objects.select_for_update().get(pk=ride_id)

    driver = DriverProfile.objects.filter(
        user=user
    ).first()

    if not driver:
        raise PermissionDenied(
            "You are not registered as a driver."
        )

    if not driver.is_available:
        raise ValidationError(
            "Driver is not available."
        )

    requested_status = get_status("REQUESTED")
    accepted_status = get_status("ACCEPTED")

    if ride.status_id != requested_status.id:
        raise ValidationError(
            "Ride is not available for acceptance."
        )

    # Ride must not already have a driver
    if ride.driver_id is not None:
        raise ValidationError(
            "Ride has already been assigned to a driver."
        )

    # Driver must not have another active ride
    conflicting_statuses = RideStatus.objects.filter(
        name__in=[
            "ACCEPTED",
            "DRIVER_ARRIVING",
            "STARTED",
        ]
    )

    if Ride.objects.filter(
        driver=driver,
        status__in=conflicting_statuses
    ).exists():
        raise ValidationError(
            "Driver already has a conflicting ride."
        )

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
        raise ValidationError(
            "Ride cannot be cancelled in its current status."
        )

    ride.status = cancelled_status

    if ride.driver:
        ride.driver.is_available = True
        ride.driver.save(update_fields=["is_available"])

    ride.save(update_fields=["status", "updated_at"])

    return ride
