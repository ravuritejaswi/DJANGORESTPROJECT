from accounts.tasks import (
    send_driver_assignment_notification,
    send_ride_completion_notification,
)
from rides.utils.helpers import get_driver_name


def notify_driver_assignment(ride):
    if ride.user and ride.driver:
        driver_name = get_driver_name(ride.driver)

        send_driver_assignment_notification.delay(
            str(ride.user.id),
            driver_name,
        )


def notify_ride_completion(ride):
    if ride.user:
        send_ride_completion_notification.delay(str(ride.user.id))
