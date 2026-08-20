from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Notification


@shared_task
def send_ride_notification(user_id, title, message):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type="ride",
        )

        return f"Ride notification created for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task
def send_driver_assignment_notification(user_id, driver_name):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        Notification.objects.create(
            user=user,
            title="Driver Assigned",
            message=f"Driver {driver_name} has been assigned to your ride.",
            notification_type="driver_assignment",
        )

        return f"Driver assignment notification created for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task
def send_ride_completion_notification(user_id):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        Notification.objects.create(
            user=user,
            title="Ride Completed",
            message="Your ride has been completed successfully.",
            notification_type="ride_completion",
        )

        return f"Ride completion notification created for {user.email}"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"


@shared_task
def send_reminder_notification(user_id, message):
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        Notification.objects.create(
            user=user,
            title="Ride Reminder",
            message=message,
            notification_type="reminder",
        )

        return f"Reminder notification created for {user.email}"

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