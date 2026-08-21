from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from accounts.models import User
from .models import DriverProfile
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .consumers import RideConsumer
from config.asgi import application
from asgiref.sync import sync_to_async
from django.test import TestCase
from accounts.models import Notification
from accounts.tasks import (
    send_ride_notification,
    send_driver_assignment_notification,
    send_ride_completion_notification,
    send_reminder_notification,
)
from .models import (
    DriverProfile,
    Vehicle,
    VehicleType,
    RideStatus,
    Ride,
    DriverLocation,
)
from .services.fare_service import calculate_fare


User = get_user_model()


class RideBusinessLogicTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create ride statuses
        self.requested_status = RideStatus.objects.create(
            name="REQUESTED"
        )

        self.accepted_status = RideStatus.objects.create(
            name="ACCEPTED"
        )

        self.cancelled_status = RideStatus.objects.create(
            name="CANCELLED"
        )

        # Create rider
        self.rider = User.objects.create_user(
            username="rider1",
            password="testpassword123"
        )

        # Create Driver A
        self.driver_user_a = User.objects.create_user(
            username="driver_a",
            email="driver_a@test.com",
            password="testpassword123"
        )

        self.driver_a = DriverProfile.objects.create(
            user=self.driver_user_a,
            license_number="LIC-A-001",
            is_available=True
        )

        # Create Driver B
        self.driver_user_b = User.objects.create_user(
            username="driver_b",
            email="driver_b@test.com",
            password="testpassword123"
        )

        self.driver_b = DriverProfile.objects.create(
            user=self.driver_user_b,
            license_number="LIC-B-001",
            is_available=True
        )

        # Create vehicle type
        self.vehicle_type = VehicleType.objects.create(
            name="Car",
            description="Test car"
        )

        # Create vehicles
        self.vehicle_a = Vehicle.objects.create(
            driver=self.driver_a,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS01AA1111",
            model="Test Car",
            color="White"
        )

        self.vehicle_b = Vehicle.objects.create(
            driver=self.driver_b,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS01BB2222",
            model="Test Car",
            color="Black"
        )

    # ---------------------------------------------------------
    # TEST 1 - FARE CALCULATION
    # ---------------------------------------------------------

    def test_fare_calculation(self):
        result = calculate_fare(
            base_fare=50,
            distance_charge=100,
            time_charge=20,
            surge_charge=30
        )

        self.assertEqual(
            result,
            Decimal("200")
        )

    # ---------------------------------------------------------
    # TEST 2 - RIDE CREATION
    # ---------------------------------------------------------

    def test_ride_creation(self):
        ride = Ride.objects.create(
            user=self.rider,
            status=self.requested_status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

        self.assertIsNotNone(ride.id)
        self.assertEqual(ride.user, self.rider)
        self.assertEqual(ride.status, self.requested_status)
        self.assertEqual(ride.fare, Decimal("200.00"))

    # ---------------------------------------------------------
    # TEST 3 - RIDE ACCEPTANCE
    # ---------------------------------------------------------

    def test_ride_acceptance(self):
        ride = Ride.objects.create(
            user=self.rider,
            status=self.requested_status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

        self.client.force_authenticate(
            user=self.driver_user_a
        )

        response = self.client.post(
            f"/api/rides/{ride.id}/accept/"
        )

        self.assertEqual(response.status_code, 200)

        ride.refresh_from_db()

        self.assertEqual(
            ride.driver,
            self.driver_a
        )

        self.assertEqual(
            ride.status,
            self.accepted_status
        )

    # ---------------------------------------------------------
    # TEST 4 - DRIVER B CANNOT ACCEPT SAME RIDE
    # ---------------------------------------------------------

    def test_second_driver_cannot_accept_same_ride(self):
        ride = Ride.objects.create(
            user=self.rider,
            status=self.requested_status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

        # Driver A accepts the ride
        self.client.force_authenticate(
            user=self.driver_user_a
        )

        response_a = self.client.post(
            f"/api/rides/{ride.id}/accept/"
        )

        self.assertEqual(
            response_a.status_code,
            200
        )

        # Driver B tries to accept the same ride
        self.client.force_authenticate(
            user=self.driver_user_b
        )

        response_b = self.client.post(
            f"/api/rides/{ride.id}/accept/"
        )

        self.assertEqual(
            response_b.status_code,
            400
        )

        ride.refresh_from_db()

        # Ride must still belong to Driver A
        self.assertEqual(
            ride.driver,
            self.driver_a
        )

    # ---------------------------------------------------------
    # TEST 5 - CANCELLATION
    # ---------------------------------------------------------

    def test_ride_cancellation(self):
        ride = Ride.objects.create(
            user=self.rider,
            status=self.requested_status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

        self.client.force_authenticate(
            user=self.rider
        )

        response = self.client.post(
            f"/api/rides/{ride.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        ride.refresh_from_db()

        self.assertEqual(
            ride.status,
            self.cancelled_status
        )

    # ---------------------------------------------------------
    # TEST 6 - INVALID STATE CHANGE
    # ---------------------------------------------------------

    def test_cannot_accept_cancelled_ride(self):
        ride = Ride.objects.create(
            user=self.rider,
            status=self.cancelled_status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

        self.client.force_authenticate(
            user=self.driver_user_a
        )

        response = self.client.post(
            f"/api/rides/{ride.id}/accept/"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        ride.refresh_from_db()

        self.assertIsNone(
            ride.driver
        )

        self.assertEqual(
            ride.status,
            self.cancelled_status
        )

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from .models import DriverProfile


class DriverTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="driveruser",
            email="driver@example.com",
            password="Test@12345"
        )
        self.client.force_authenticate(user=self.user)

        self.driver_url = reverse("drivers-list")

        self.driver_data = {
            "user": str(self.user.id),
            "license_number": "DL123456789",
            "is_available": True
        }

    def test_create_driver(self):
        response = self.client.post(
            self.driver_url,
            self.driver_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            DriverProfile.objects.filter(
                license_number="DL123456789"
            ).exists()
        )

    def test_list_drivers(self):
        DriverProfile.objects.create(
            user=self.user,
            license_number="DL987654321",
            is_available=True
        )

        response = self.client.get(self.driver_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["count"],
            1
        )

    def test_retrieve_driver(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL111111111",
            is_available=True
        )

        url = reverse(
            "drivers-detail",
            kwargs={"pk": driver.id}
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["license_number"],
            "DL111111111"
        )

    def test_update_driver(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL222222222",
            is_available=False
        )

        url = reverse(
            "drivers-detail",
            kwargs={"pk": driver.id}
        )

        response = self.client.patch(
            url,
            {
                "is_available": True
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        driver.refresh_from_db()

        self.assertTrue(
            driver.is_available
        )

    def test_delete_driver(self):
        driver = DriverProfile.objects.create(
            user=self.user,
            license_number="DL123456789",
            is_available=True
        )

        url = reverse(
            "drivers-detail",
            kwargs={"pk": driver.id}
        )
        response = self.client.delete(url)
        print("DELETE URL:", url)
        print("DELETE STATUS:", response.status_code)
        print("DELETE DATA:", response.data)
        print("ALLOWED METHODS:", response.headers.get("Allow"))

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            DriverProfile.objects.filter(
                id=driver.id
            ).exists()
        )

    def test_create_driver_invalid_data(self):
        response = self.client.post(
            self.driver_url,
            {
                "user": str(self.user.id),
                "license_number": "",
                "is_available": True
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )


class VehicleTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.driver_user = User.objects.create_user(
            username="vehicle_driver",
            email="vehicle_driver@test.com",
            password="testpassword123"
        )

        self.other_driver_user = User.objects.create_user(
            username="other_driver",
            email="other_driver@test.com",
            password="testpassword123"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="LIC-VEH-001",
            is_available=True
        )

        self.other_driver = DriverProfile.objects.create(
            user=self.other_driver_user,
            license_number="LIC-VEH-002",
            is_available=True
        )

        self.vehicle_type = VehicleType.objects.create(
            name="Test Car",
            description="Test vehicle"
        )

        self.client.force_authenticate(
            user=self.driver_user
        )

    def test_create_vehicle_success(self):
        data = {
            "driver": str(self.driver.id),
            "vehicle_type": str(self.vehicle_type.id),
            "vehicle_number": "TS09TEST1234",
            "model": "Swift",
            "color": "White",
            "is_active": True
        }

        response = self.client.post(
            "/api/vehicles/",
            data,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_201_CREATED, status.HTTP_200_OK]
        )

        self.assertTrue(
            Vehicle.objects.filter(
                vehicle_number="TS09TEST1234"
            ).exists()
        )

    def test_duplicate_vehicle_number(self):
        Vehicle.objects.create(
            driver=self.driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09DUP1234",
            model="Swift",
            color="White"
        )

        data = {
            "driver": str(self.driver.id),
            "vehicle_type": str(self.vehicle_type.id),
            "vehicle_number": "TS09DUP1234",
            "model": "Honda",
            "color": "Black",
            "is_active": True
        }

        response = self.client.post(
            "/api/vehicles/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_driver_cannot_manage_other_drivers_vehicle(self):
        vehicle = Vehicle.objects.create(
            driver=self.other_driver,
            vehicle_type=self.vehicle_type,
            vehicle_number="TS09OTHER123",
            model="Honda",
            color="Black"
        )

        data = {
            "driver": str(self.other_driver.id),
            "vehicle_type": str(self.vehicle_type.id),
            "vehicle_number": "TS09CHANGE123",
            "model": "Honda",
            "color": "Red",
            "is_active": True
        }

        response = self.client.put(
            f"/api/vehicles/{vehicle.id}/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_vehicle_without_authentication(self):
        self.client.force_authenticate(user=None)

        data = {
            "driver": str(self.driver.id),
            "vehicle_type": str(self.vehicle_type.id),
            "vehicle_number": "TS09NOAUTH123",
            "model": "Swift",
            "color": "White",
            "is_active": True
        }

        response = self.client.post(
            "/api/vehicles/",
            data,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ]
        )

class DriverLocationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="locationdriver",
            email="locationdriver@example.com",
            password="Test@12345"
        )

        self.driver = DriverProfile.objects.create(
            user=self.user,
            license_number="LOC-LIC-001",
            is_available=True
        )

        self.location_url = reverse("driver-location")

    def test_create_driver_location_success(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.location_url,
            {
                "latitude": "17.385044",
                "longitude": "78.486671"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            DriverLocation.objects.filter(
                driver=self.driver
            ).exists()
        )

        location = DriverLocation.objects.get(
            driver=self.driver
        )

        self.assertEqual(
            str(location.latitude),
            "17.385044"
        )

        self.assertEqual(
            str(location.longitude),
            "78.486671"
        )

    def test_update_driver_location_success(self):
        DriverLocation.objects.create(
            driver=self.driver,
            latitude="17.385044",
            longitude="78.486671"
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.location_url,
            {
                "latitude": "17.400000",
                "longitude": "78.500000"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        location = DriverLocation.objects.get(
            driver=self.driver
        )

        self.assertEqual(
            str(location.latitude),
            "17.400000"
        )

        self.assertEqual(
            str(location.longitude),
            "78.500000"
        )

    def test_driver_location_without_authentication(self):
        self.client.force_authenticate(
            user=None
        )

        response = self.client.post(
            self.location_url,
            {
                "latitude": "17.385044",
                "longitude": "78.486671"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class PermissionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="permissionuser",
            email="permission@example.com",
            password="Test@12345"
        )

        self.driver_user = User.objects.create_user(
            username="permissiondriver",
            email="driverpermission@example.com",
            password="Test@12345"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="PERM-LIC-001",
            is_available=True
        )

        self.url = reverse("drivers-list")

    def test_authenticated_user_has_permission(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_authenticated_driver_has_permission(self):
        self.client.force_authenticate(
            user=self.driver_user
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthenticated_user_denied(self):
        self.client.force_authenticate(
            user=None
        )

        location_url = reverse("driver-location")

        response = self.client.post(
            location_url,
            {
                "latitude": "17.385044",
                "longitude": "78.486671"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class RideWebSocketTests(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="wsuser",
            email="wsuser@example.com",
            password="Test@12345"
        )

        self.other_user = User.objects.create_user(
            username="otherwsuser",
            email="otherwsuser@example.com",
            password="Test@12345"
        )

        self.driver_user = User.objects.create_user(
            username="wsdriver",
            email="wsdriver@example.com",
            password="Test@12345"
        )

        self.driver = DriverProfile.objects.create(
            user=self.driver_user,
            license_number="WS-LIC-001",
            is_available=True
        )

        self.status = RideStatus.objects.create(
            name="REQUESTED"
        )

        self.ride = Ride.objects.create(
            user=self.user,
            driver=self.driver,
            status=self.status,
            pickup_address="Hyderabad",
            drop_address="Secunderabad",
            pickup_latitude=Decimal("17.385044"),
            pickup_longitude=Decimal("78.486671"),
            drop_latitude=Decimal("17.439930"),
            drop_longitude=Decimal("78.498274"),
            ride_type="NOW",
            fare=Decimal("200.00")
        )

    @sync_to_async
    def get_access_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    async def test_valid_rider_connection(self):
        access_token = await self.get_access_token(self.user)
        
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/?token={access_token}"
        )

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_missing_token_rejected(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/"
        )

        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

    async def test_invalid_token_rejected(self):
        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/?token=invalid-token"
        )

        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

    async def test_unauthorized_user_rejected(self):
        access_token = await self.get_access_token(self.other_user)

        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/?token={access_token}"
        )

        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4003)

    async def test_driver_can_connect(self):
        access_token = await self.get_access_token(self.driver_user)

        communicator = WebsocketCommunicator(
            application,
            f"/ws/rides/{self.ride.id}/?token={access_token}"
        )

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

class FareTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="fareuser",
            email="fare@example.com",
            password="Test@12345"
        )

        self.status = RideStatus.objects.create(
            name="REQUESTED"
        )

        self.ride = Ride.objects.create(
            user=self.user,
            status=self.status,
            pickup_address="Hyderabad",
            drop_address="Warangal",
            pickup_latitude=17.3850,
            pickup_longitude=78.4867,
            drop_latitude=17.9689,
            drop_longitude=79.5941,
            ride_type="NOW",
            fare=150.00
        )

        self.fare_url = reverse(
            "rides-fare",
            kwargs={"pk": self.ride.id}
        )

    def test_fare_calculation_success(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.fare_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["base_fare"],
            40
        )

        self.assertEqual(
            response.data["distance_fare"],
            80
        )

        self.assertEqual(
            response.data["time_fare"],
            20
        )

        self.assertEqual(
            response.data["surge"],
            10
        )

        self.assertEqual(
            response.data["total"],
            150
        )

    def test_fare_without_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.fare_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_fare_for_invalid_ride(self):
        self.client.force_authenticate(user=self.user)

        invalid_url = reverse(
            "rides-fare",
            kwargs={
                "pk": "00000000-0000-0000-0000-000000000000"
            }
        )

        response = self.client.get(invalid_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

class NotificationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="notificationuser",
            email="notification@example.com",
            password="Test@12345"
        )

    def test_send_ride_notification_success(self):
        result = send_ride_notification.run(
            self.user.id,
            "Ride Requested",
            "Your ride has been requested successfully."
        )

        self.assertEqual(
            result,
            "Ride notification created for notification@example.com"
        )

        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                title="Ride Requested",
                message="Your ride has been requested successfully.",
                notification_type="ride"
            ).exists()
        )

    def test_send_driver_assignment_notification_success(self):
        result = send_driver_assignment_notification.run(
            self.user.id,
            "John"
        )

        self.assertEqual(
            result,
            "Driver assignment notification created for notification@example.com"
        )

        notification = Notification.objects.get(
            user=self.user,
            notification_type="driver_assignment"
        )

        self.assertEqual(
            notification.title,
            "Driver Assigned"
        )

        self.assertEqual(
            notification.message,
            "Driver John has been assigned to your ride."
        )

    def test_send_ride_completion_notification_success(self):
        result = send_ride_completion_notification.run(
            self.user.id
        )

        self.assertEqual(
            result,
            "Ride completion notification created for notification@example.com"
        )

        notification = Notification.objects.get(
            user=self.user,
            notification_type="ride_completion"
        )

        self.assertEqual(
            notification.title,
            "Ride Completed"
        )

        self.assertEqual(
            notification.message,
            "Your ride has been completed successfully."
        )

    def test_send_reminder_notification_success(self):
        result = send_reminder_notification.run(
            self.user.id,
            "Your ride starts in 30 minutes."
        )

        self.assertEqual(
            result,
            "Reminder notification created for notification@example.com"
        )

        notification = Notification.objects.get(
            user=self.user,
            notification_type="reminder"
        )

        self.assertEqual(
            notification.title,
            "Ride Reminder"
        )

        self.assertEqual(
            notification.message,
            "Your ride starts in 30 minutes."
        )

    def test_notification_for_invalid_user(self):
        invalid_user_id = 999999

        result = send_ride_notification.run(
            invalid_user_id,
            "Test",
            "Test notification"
        )

        self.assertEqual(
            result,
            f"User {invalid_user_id} does not exist"
        )

        self.assertFalse(
            Notification.objects.filter(
                title="Test",
                message="Test notification"
            ).exists()
        )

class SecurityTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_ride_access(self):
        response = self.client.get("/api/rides/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthorized_vehicle_access(self):
        response = self.client.get("/api/drivers/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_invalid_jwt(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid.jwt.token"
        )

        response = self.client.get("/api/drivers/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_user_accessing_another_users_ride(self):
        # Create two users
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="Test@12345"
        )

        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="Test@12345"
        )

        # Create ride status
        ride_status = RideStatus.objects.create(
            name="REQUESTED"
        )

        # Create a ride belonging to user1
        ride = Ride.objects.create(
            user=user1,
            status=ride_status,
            pickup_address="Hyderabad",
            drop_address="Warangal",
            pickup_latitude=17.385044,
            pickup_longitude=78.486671,
            drop_latitude=17.968901,
            drop_longitude=79.594055,
            ride_type="NOW",
            fare=500.00
        )

        # Authenticate as user2
        self.client.force_authenticate(user=user2)

        # Try to access user1's ride
        response = self.client.get(
            f"/api/rides/{ride.id}/"
        )

        # User2 should not be allowed
        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND
            ]
        )
    def test_driver_cannot_access_another_drivers_data(self):
        driver_user_1 = User.objects.create_user(
            username="driveruser1",
            email="driver1@example.com",
            password="Test@12345"
        )

        driver_user_2 = User.objects.create_user(
            username="driveruser2",
            email="driver2@example.com",
            password="Test@12345"
        )

        driver_1 = DriverProfile.objects.create(
            user=driver_user_1,
            license_number="SEC-LIC-001",
            is_available=True
        )

        DriverProfile.objects.create(
            user=driver_user_2,
            license_number="SEC-LIC-002",
            is_available=True
        )

        # Authenticate as Driver 2
        self.client.force_authenticate(
            user=driver_user_2
        )

        # Driver 2 tries to access Driver 1's profile
        response = self.client.get(
            f"/api/drivers/{driver_1.id}/"
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_403_FORBIDDEN,
                status.HTTP_404_NOT_FOUND
            ]
        )
    async def test_invalid_websocket_token(self):
        from channels.testing import WebsocketCommunicator
        from config.asgi import application

        communicator = WebsocketCommunicator(
            application,
            "/ws/rides/00000000-0000-0000-0000-000000000000/?token=invalid-token"
        )

        connected, close_code = await communicator.connect()

        self.assertFalse(connected)
        self.assertEqual(close_code, 4001)

    def test_invalid_ride_payload(self):
        user = User.objects.create_user(
            username="payloaduser",
            email="payload@example.com",
            password="Test@12345"
        )

        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/rides/",
            {
                "pickup_address": "",
                "drop_address": "",
                "pickup_latitude": "invalid",
                "pickup_longitude": "invalid",
                "drop_latitude": "invalid",
                "drop_longitude": "invalid",
                "ride_type": "INVALID",
                "scheduled_at": None,
                "fare": "-500"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
    def test_excessive_api_requests_are_throttled(self):
        user = User.objects.create_user(
            username="throttleuser",
            email="throttle@example.com",
            password="Test@12345"
        )

        self.client.force_authenticate(user=user)

        responses = []

        for _ in range(35):
            response = self.client.get("/api/drivers/")
            responses.append(response.status_code)

        self.assertIn(
            status.HTTP_429_TOO_MANY_REQUESTS,
            responses
        )