from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    DriverProfile,
    Vehicle,
    VehicleType,
    RideStatus,
    Ride,
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

# Create your tests here.
