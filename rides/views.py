from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .services.fare_service import calculate_fare
from rest_framework.permissions import IsAuthenticated
from rides.services.ride_service import (accept_ride as accept_ride_service, cancel_ride as cancel_ride_service,)
from .models import DriverProfile, Ride, RideStatus
from rest_framework.exceptions import ValidationError
from core.responses import error_response
from .serializers import (
    DriverProfileSerializer,
    RideSerializer,
    RideStatusUpdateSerializer,
)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all().order_by("-created_at")
    serializer_class = DriverProfileSerializer

    def destroy(self, request, *args, **kwargs):
        driver = self.get_object()
        driver.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class RideViewSet(viewsets.ModelViewSet):
    queryset = (
    Ride.objects
    .select_related("user", "driver", "vehicle", "status")
    .order_by("-created_at")
    )
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
        ride = accept_ride_service(
            ride_id=pk,
            user=request.user
        )

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_ride(self, request, pk=None):
        try:
            ride = cancel_ride_service(pk)

            return Response(
                RideSerializer(ride).data,
                status=status.HTTP_200_OK
            )

        except ValidationError:
            return error_response(
                "Ride cannot be cancelled",
                "INVALID_RIDE_STATUS",
                status.HTTP_400_BAD_REQUEST
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

    @action(detail=True, methods=["get"], url_path="fare")
    def fare(self, request, pk=None):
        ride = self.get_object()

        base_fare = 40
        distance_fare = 80
        time_fare = 20
        surge = 10

        total = calculate_fare(
            base_fare,
            distance_fare,
            time_fare,
            surge,
        )

        return Response({
            "base_fare": base_fare,
            "distance_fare": distance_fare,
            "time_fare": time_fare,
            "surge": surge,
            "total": total,
        }, status=status.HTTP_200_OK)