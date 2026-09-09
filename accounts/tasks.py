from datetime import timedelta
import uuid
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from .models import Notification
from rides.models import Ride

@shared_task(queue="notifications")
def send_ride_notification(user_id, title, message, event_id=None):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        event_id = event_id or str(uuid.uuid4())

        notification, created = Notification.objects.get_or_create(
            user=user,
            event_id=event_id,
            defaults={
                "title": title,
                "message": message,
                "notification_type": "ride",
            },
        )

        if created:
            return f"Ride notification created for {user.email}"

        return f"Ride notification already exists for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task(queue="notifications")
def send_driver_assignment_notification(user_id, driver_name, event_id=None):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        event_id = event_id or str(uuid.uuid4())

        notification, created = Notification.objects.get_or_create(
            user=user,
            event_id=event_id,
            defaults={
                "title": "Driver Assigned",
                "message": f"Driver {driver_name} has been assigned to your ride.",
                "notification_type": "driver_assignment",
            },
        )
        if created:
            return f"Driver assignment notification created for {user.email}"

        return f"Driver assignment notification already exists for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task(queue="notifications")
def send_ride_completion_notification(user_id, event_id=None):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        event_id = event_id or str(uuid.uuid4())

        event_id = event_id or str(uuid.uuid4())

        notification, created = Notification.objects.get_or_create(
            user=user,
            event_id=event_id,
            defaults={
                "title": "Ride Completed",
                "message": "Your ride has been completed successfully.",
                "notification_type": "ride_completion",
            },
        )
        if created:
            return f"Ride completion notification created for {user.email}"

        return f"Ride completion notification already exists for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task(queue="notifications")
def send_reminder_notification(user_id, message, event_id=None):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        event_id = event_id or str(uuid.uuid1())
        notification, created = Notification.objects.get_or_create(
            user=user,
            event_id=event_id,
            defaults={
                "title": "Ride Reminder",
                "message": message,
                "notification_type": "reminder",
            },
        )
        if created:
            return f"Reminder notification created for {user.email}"

        return f"Reminder notification already exists for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"



@shared_task(bind=True, max_retries=2)
def retry_test_job(self):
    attempt = self.request.retries + 1

    print(f"Attempt {attempt}")

    if attempt < 3:
        print(f"Attempt {attempt} failed. Retrying...")
        raise self.retry(
            exc=Exception(f"Attempt {attempt} failed"),
            countdown=2
        )

    print("Attempt 3 succeeded!")
    return {
        "success": True,
        "attempt": attempt,
        "message": "Job completed successfully on attempt 3"
    }

@shared_task
def failed_test():
    raise Exception("Test Failure")

@shared_task(queue="reports")
def generate_ride_report():
    total_rides = Ride.objects.count()

    completed_rides = Ride.objects.filter(
        status__name="COMPLETED"
    ).count()

    cancelled_rides = Ride.objects.filter(
        status__name="CANCELLED"
    ).count()

    total_fare = Ride.objects.filter(
        status__name="COMPLETED"
    ).aggregate(
        total=Sum("fare")
    )["total"] or 0

    return {
        "total_rides": total_rides,
        "completed_rides": completed_rides,
        "cancelled_rides": cancelled_rides,
        "total_fare": str(total_fare),
    }

@shared_task(queue="maintenance")
def clean_expired_data(days=30):
    cutoff_date = timezone.now() - timedelta(days=days)

    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=cutoff_date,
    ).delete()

    return {
        "deleted_notifications": deleted_count,
        "older_than_days": days,
    }

@shared_task(queue="maintenance")
def process_background_records():
    requested_rides = Ride.objects.filter(
        status__name="REQUESTED"
    )

    processed_count = requested_rides.count()

    return {
        "processed_records": processed_count,
        "record_type": "requested_rides",
    }

@shared_task(queue="maintenance")
def clean_old_temporary_data():
    from django.core.management import call_command

    call_command("clearsessions")

    return "Expired session data cleaned successfully"