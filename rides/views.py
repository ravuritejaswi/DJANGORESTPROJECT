from django.db.migrations import serializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DriverProfile, Ride, RideStatus, DriverProfile
from .serializers import (
    DriverProfileSerializer,
    RideSerializer,
    RideStatusUpdateSerializer,
)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all().order_by("-created_at")
    serializer_class = DriverProfileSerializer

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all().order_by("-created_at")
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        requested_status = RideStatus.objects.get(name="REQUESTED")

        serializer.save(
            user=self.request.user,
            status=requested_status,
            driver=serializer.validated_data.get("driver"),
            vehicle=serializer.validated_data.get("vehicle"),
        )

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        ride = self.get_object()

        serializer = RideStatusUpdateSerializer(
            ride,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )
    @action(detail=True, methods=["post"], url_path="accept")
    def accept_ride(self, request, pk=None):
        ride = self.get_object()

        # Get driver profile of logged-in user
        driver = DriverProfile.objects.filter(
            user=request.user
        ).first()

        if not driver:
            return Response(
                {"detail": "You are not registered as a driver."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check driver is available
        if not driver.is_available:
            return Response(
                {"detail": "Driver is not available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check ride is still available
        requested_status = RideStatus.objects.get(name="REQUESTED")
        accepted_status = RideStatus.objects.get(name="ACCEPTED")

        if ride.status_id != requested_status.id:
            return Response(
                {"detail": "Ride is not available for acceptance."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ride.driver_id is not None:
            return Response(
                {"detail": "Ride has already been assigned to a driver."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check driver has a conflicting active ride
        conflicting_statuses = RideStatus.objects.filter(
            name__in=["ACCEPTED", "DRIVER_ARRIVING", "STARTED"]
        )

        if Ride.objects.filter(
            driver=driver,
            status__in=conflicting_statuses
        ).exists():
            return Response(
                {"detail": "Driver already has a conflicting ride."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Assign driver and accept ride
        ride.driver = driver
        ride.status = accepted_status
        ride.save(update_fields=["driver", "status", "updated_at"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_ride(self, request, pk=None):
        ride = self.get_object()

        cancelled_status = RideStatus.objects.get(name="CANCELLED")

    # Ride can be cancelled only before completion
        if ride.status.name in ["COMPLETED", "CANCELLED"]:
            return Response(
                {"detail": "Ride cannot be cancelled in its current status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ride.status = cancelled_status

    # If a driver had accepted the ride, make the driver available again
        if ride.driver:
            ride.driver.is_available = True
            ride.driver.save(update_fields=["is_available"])

        ride.save(update_fields=["status", "updated_at"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="start")
    def start_ride(self, request, pk=None):
        ride = self.get_object()

        started_status = RideStatus.objects.get(name="STARTED")

    # Ride can be started only after it is accepted
        if ride.status.name != "ACCEPTED":
            return Response(
                {"detail": "Ride cannot be started in its current status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ride.status = started_status
        ride.save(update_fields=["status", "updated_at"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_ride(self, request, pk=None):
        ride = self.get_object()

        completed_status = RideStatus.objects.get(name="COMPLETED")

        # Ride can be completed only after it is started
        if ride.status.name != "STARTED":
            return Response(
                {"detail": "Ride cannot be completed in its current status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ride.status = completed_status
        ride.save(update_fields=["status", "updated_at"])

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )