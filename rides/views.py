from django.db.migrations import serializer
from django.http import request
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from api.views import drivers
from .services.fare_service import calculate_fare
from rest_framework.permissions import IsAuthenticated
from rides.services.ride_service import (accept_ride as accept_ride_service, cancel_ride as cancel_ride_service,)
from .models import DriverProfile, Ride, RideStatus, DriverLocation
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Count, Avg, Max, Sum
from django.db import connection
import math
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from core.responses import error_response
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    DriverProfileSerializer,
    RideSerializer,
    RideStatusUpdateSerializer,
    DriverLocationSerializer,
)

def broadcast_ride_status(ride):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"ride_{ride.id}",
        {
            "type": "ride_status",
            "ride_id": str(ride.id),
            "status": ride.status.name,
        }
    )

class DriverViewSet(viewsets.ModelViewSet):
    queryset = (
        DriverProfile.objects
        .select_related("user")
        .order_by("-created_at")
    )
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
        print("UPDATE STATUS CALLED")
        print("REQUEST DATA:", request.data)
        print("RIDE ID:", pk)
        ride = self.get_object()

        serializer = RideStatusUpdateSerializer(
            ride,
            data=request.data,
            partial=True
        )
        print("BEFORE SERIALIZER VALIDATION")
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("SERIALIZER ERROR:", repr(e))
            raise
        print("SERIALIZER VALIDATED PASSED")
        serializer.save()
        print("SERIALIZER SAVED PASSED")
        ride.refresh_from_db()

        broadcast_ride_status(ride)

        return Response(
            RideSerializer(ride).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["patch"], url_path="location")
    def update_location(self, request, pk=None):
        ride = self.get_object()

        if ride.driver is None:
            return Response(
                {"detail": "No driver assigned to this ride."},
                status=status.HTTP_400_BAD_REQUEST
            )

        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude is None or longitude is None:
            return Response(
                {"detail": "latitude and longitude are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        location, _ = DriverLocation.objects.update_or_create(
            driver=ride.driver,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
            }
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"ride_{ride.id}",
            {
                "type": "driver_location",
                "ride_id": str(ride.id),
                "latitude": str(location.latitude),
                "longitude": str(location.longitude),
            }
        )

        return Response(
            DriverLocationSerializer(location).data,
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
        broadcast_ride_status(ride)
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
        broadcast_ride_status(ride)
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

class UserActiveRidesView(APIView):
    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user
        ).filter(
            Q(status__name="REQUESTED") |
            Q(status__name="ACCEPTED") |
            Q(status__name="DRIVER_ARRIVING") |
            Q(status__name="STARTED")
        )

        return Response({
            "count": rides.count(),
            "rides": list(
                rides.values(
                    "id",
                    "pickup_address",
                    "drop_address",
                    "fare",
                    "created_at"
                )
            )
        })

class CompletedRidesView(APIView):

    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user,
            status__name="COMPLETED"
        )

        return Response({
            "count": rides.count(),
            "rides": list(
                rides.values(
                    "id",
                    "pickup_address",
                    "drop_address",
                    "fare",
                    "created_at"
                )
            )
        })

class CancelledRidesView(APIView):

    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user,
            status__name="CANCELLED"
        )

        return Response({
            "count": rides.count(),
            "rides": list(
                rides.values(
                    "id",
                    "pickup_address",
                    "drop_address",
                    "fare",
                    "created_at"
                )
            )
        })

class DriverRideHistoryView(APIView):

    def get(self, request):
        rides = Ride.objects.filter(
            driver__user=request.user
        ).order_by("-created_at")

        return Response({
            "count": rides.count(),
            "rides": list(
                rides.values(
                    "id",
                    "pickup_address",
                    "drop_address",
                    "fare",
                    "status__name",
                    "created_at"
                )
            )
        })

class DailyRideCountView(APIView):

    def get(self, request):
        data = (
            Ride.objects
            .filter(user=request.user)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(ride_count=Count("id"))
            .order_by("-day")
        )

        return Response(data)

class TotalCompletedRidesView(APIView):

    def get(self, request):

        total = Ride.objects.filter(
            user=request.user,
            status__name="COMPLETED"
        ).count()

        return Response({
            "total_completed_rides": total
        })

class TotalFareEarnedView(APIView):

    def get(self, request):

        result = Ride.objects.filter(
            driver__user=request.user,
            status__name="COMPLETED"
        ).aggregate(
            total_fare=Sum("fare")
        )

        return Response(result)

class RideAggregationsView(APIView):
    def get(self, request):
        result = Ride.objects.aggregate(
            total_rides=Count("id"),
            completed_rides=Count(
                "id",
                filter=Q(status__name="COMPLETED")
            ),
            cancelled_rides=Count(
                "id",
                filter=Q(status__name="CANCELLED")
            ),
            average_fare=Avg("fare"),
            maximum_fare=Max("fare"),
        )

        return Response(result)


class SlowRideQueryView(APIView):

    def get(self, request):

        connection.queries_log.clear()

        rides = Ride.objects.select_related(
            "user",
            "driver",
            "vehicle",
            "status"
        )

        data = []

        for ride in rides:
            data.append({
                "id": str(ride.id),
                "user": str(ride.user),
                "driver": str(ride.driver) if ride.driver else None,
                "vehicle": str(ride.vehicle) if ride.vehicle else None,
                "status": str(ride.status),
                "fare": float(ride.fare),
            })

        return Response({
            "rides": data,
            "sql_queries": len(connection.queries),
        })

class AdvancedRideFilterView(APIView):

    def get(self, request):

        rides = Ride.objects.select_related(
            "user",
            "driver",
            "vehicle",
            "status"
        )

        # 1. Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            rides = rides.filter(created_at__date__gte=start_date)

        if end_date:
            rides = rides.filter(created_at__date__lte=end_date)

        # 2. Status filtering
        status_name = request.query_params.get("status")

        if status_name:
            rides = rides.filter(status__name__iexact=status_name)

        # 3. Driver filtering
        driver_id = request.query_params.get("driver_id")

        if driver_id:
            rides = rides.filter(driver_id=driver_id)

        # 4. Fare range filtering
        min_fare = request.query_params.get("min_fare")
        max_fare = request.query_params.get("max_fare")

        if min_fare:
            rides = rides.filter(fare__gte=min_fare)

        if max_fare:
            rides = rides.filter(fare__lte=max_fare)

        # 5. Ordering
        ordering = request.query_params.get("ordering", "-created_at")

        allowed_ordering = [
            "created_at",
            "-created_at",
            "fare",
            "-fare",
        ]

        if ordering not in allowed_ordering:
            ordering = "-created_at"

        rides = rides.order_by(ordering)

        serializer = RideSerializer(rides, many=True)

        return Response({
            "count": rides.count(),
            "rides": serializer.data
        })

class LargeDatasetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeDatasetRideView(APIView):

    def get(self, request):

        rides = (
            Ride.objects.select_related(
                "user",
                "driver",
                "vehicle",
                "status"
            )
            .order_by("-created_at")
        )

        paginator = LargeDatasetPagination()

        page = paginator.paginate_queryset(rides, request)

        serializer = RideSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

class DriverLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver = request.user.driver_profile

        location, created = DriverLocation.objects.update_or_create(
            driver=driver,
            defaults={
                "latitude": request.data.get("latitude"),
                "longitude": request.data.get("longitude"),
            }
        )

        serializer = DriverLocationSerializer(location)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class NearbyDriverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        radius = request.GET.get("radius")

    # Missing coordinates
        if latitude is None or longitude is None:
            return Response(
                {"error": "latitude and longitude are required"},
                status=400
            )

    # Missing radius
        if radius is None:
            return Response(
                {"error": "radius is required"},
                status=400
            )

    # Convert values safely
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except (TypeError, ValueError):
            return Response(
                {"error": "latitude, longitude and radius must be valid numbers"},
                status=400
            )

    # Validate latitude
        if latitude < -90 or latitude > 90:
            return Response(
                {"error": "Invalid latitude"},
                status=400
            )

    # Validate longitude
        if longitude < -180 or longitude > 180:
            return Response(
                {"error": "Invalid longitude"},
                status=400
            )

    # Validate radius
        if radius <= 0:
            return Response(
                {"error": "Invalid radius"},
                status=400
            )

    # Only active ONLINE drivers
        drivers = DriverLocation.objects.filter(
        availability_status="ONLINE",
        is_available=True
        ).values("driver_id", "latitude", "longitude")

        nearby_drivers = []
        for driver in drivers:
            distance = self.calculate_distance(
                latitude,
                longitude,
                float(driver["latitude"]),
                float(driver["longitude"])
            )
            if distance <= radius:
                nearby_drivers.append({
                    "driver_id": str(driver["driver_id"]),
                    "distance_km": round(distance, 2)
                })
        nearby_drivers.sort(key=lambda x: x["distance_km"])
        return Response(nearby_drivers)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371.0

        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return R * c