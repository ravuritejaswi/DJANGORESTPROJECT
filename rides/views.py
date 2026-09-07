from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import connection
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import TruncDate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.core.cache import cache
from core.responses import error_response, success_response
from rides.services.driver_service import (find_nearby_drivers,
                                           update_driver_location)
from rides.services.notification_service import notify_driver_assignment
from rides.services.ride_service import accept_ride as accept_ride_service
from rides.services.ride_service import cancel_ride as cancel_ride_service
from rides.services.ride_service import complete_ride as complete_ride_service
from rides.services.ride_service import create_ride as create_ride_service
from rides.services.ride_service import start_ride as start_ride_service

from .models import DriverLocation, DriverProfile, Ride, Vehicle, VehicleType
from .permissions import (IsOwnDriverProfile,
                          IsRideOwnerOrDriver)
from .serializers import (DriverLocationSerializer, DriverProfileSerializer,
                          RideSerializer, RideStatusUpdateSerializer,
                          VehicleSerializer, VehicleTypeSerializer)
from .services.fare_service import get_ride_fare


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
    permission_classes = [
        IsAuthenticated,
        IsOwnDriverProfile,
    ]

    def destroy(self, request, *args, **kwargs):
        driver = self.get_object()
        driver.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = (
        Vehicle.objects
        .select_related("driver", "vehicle_type")
        .order_by("-created_at")
    )

    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

class RideViewSet(viewsets.ModelViewSet):
    queryset = (
    Ride.objects
    .select_related("user", "driver", "vehicle", "status")
    .order_by("-created_at")
    )
    serializer_class = RideSerializer
    permission_classes = [
        IsAuthenticated,
        IsRideOwnerOrDriver,
    ]
    
    def perform_create(self, serializer):
        ride = create_ride_service(
            user=self.request.user,
            validated_data=serializer.validated_data,
        )

        serializer.instance = ride

    @swagger_auto_schema(
        operation_summary="Update ride status",
        operation_description="Updates the status of an existing ride.",
        request_body=RideStatusUpdateSerializer,
        responses={
            200: "Ride status updated successfully",
            400: "Invalid ride status or request data",
            401: "Authentication required",
            404: "Ride not found",
        },
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

        return success_response(
            message="Ride status updated successfully",
            data=RideSerializer(ride).data,
            status_code=status.HTTP_200_OK,
        )
    @swagger_auto_schema(
        operation_summary="Update driver location",
        operation_description=(
            "Updates the driver's latitude and longitude "
            "for the selected ride."
        ),
        request_body=DriverLocationSerializer,
        responses={
            200: "Driver location updated successfully",
            201: "Driver location created successfully",
            400: "Invalid location or no driver assigned",
            401: "Authentication required",
            404: "Ride not found",
        },
    )

    @action(detail=True, methods=["patch"], url_path="location")
    def update_location(self, request, pk=None):
        ride = self.get_object()

        if ride.driver is None:
            return Response(
                {"detail": "No driver assigned to this ride."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            location, created = update_driver_location(
                driver=ride.driver,
                latitude=request.data.get("latitude"),
                longitude=request.data.get("longitude"),
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc.detail)},
                status=status.HTTP_400_BAD_REQUEST
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

        return success_response(
            message=(
                "Driver location created successfully"
                if created
                else "Driver location updated successfully"
            ),
            data=DriverLocationSerializer(location).data,
            status_code=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )

    @swagger_auto_schema(
        operation_summary="Accept a ride",
        operation_description=(
            "Allows an available driver to accept a requested ride."
        ),
        responses={
            200: "Ride accepted successfully",
            400: "Ride cannot be accepted",
            401: "Authentication required",
            403: "Driver is not authorized or available",
            404: "Ride not found",
        },
    )
    
    @action(detail=True, methods=["post"], url_path="accept")
    def accept_ride(self, request, pk=None):
        ride = accept_ride_service(
            ride_id=pk,
            user=request.user
        )

        notify_driver_assignment(ride)

        return success_response(
            message="Ride accepted successfully",
            data=RideSerializer(ride).data,
            status_code=status.HTTP_200_OK,
        )
    @swagger_auto_schema(
        operation_summary="Cancel a ride",
        operation_description=(
            "Cancels an existing ride that is not already completed or cancelled."
        ),
        responses={
            200: "Ride cancelled successfully",
            400: "Ride cannot be cancelled",
            401: "Authentication required",
            404: "Ride not found",
        },
    )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_ride(self, request, pk=None):
        try:
            ride = cancel_ride_service(pk)

            return success_response(
                message="Ride cancelled successfully",
                data=RideSerializer(ride).data,
                status_code=status.HTTP_200_OK,
            )

        except ValidationError:
            return error_response(
                "Ride cannot be cancelled",
                "INVALID_RIDE_STATUS",
                status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Start a ride",
        operation_description="Starts a ride that has been accepted by a driver.",
        responses={
            200: "Ride started successfully",
            400: "Ride cannot be started",
            401: "Authentication required",
            404: "Ride not found",
        },
    )

    @action(detail=True, methods=["post"], url_path="start")
    def start_ride(self, request, pk=None):
        try:
            ride = start_ride_service(pk)

        except ValidationError as exc:
            return error_response(
                message=str(exc.detail),
                error_code="INVALID_RIDE_STATUS",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        broadcast_ride_status(ride)

        return success_response(
            message="Ride started successfully",
            data=RideSerializer(ride).data,
            status_code=status.HTTP_200_OK,
        )
    @swagger_auto_schema(
        operation_summary="Complete a ride",
        operation_description="Completes a ride that is currently in progress.",
        responses={
            200: "Ride completed successfully",
            400: "Ride cannot be completed",
            401: "Authentication required",
            404: "Ride not found",
        },
    )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete_ride(self, request, pk=None):
        try:
            ride = complete_ride_service(pk)

        except ValidationError as exc:
            return error_response(
                message=str(exc.detail),
                error_code="INVALID_RIDE_STATUS",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        broadcast_ride_status(ride)

        return success_response(
            message="Ride completed successfully",
            data=RideSerializer(ride).data,
            status_code=status.HTTP_200_OK,
        )
    @swagger_auto_schema(
        operation_summary="Calculate ride fare",
        operation_description="Returns the fare information for a ride.",
        responses={
            200: "Fare calculated successfully",
            401: "Authentication required",
            404: "Ride not found",
        },
    )

    @action(detail=True, methods=["get"], url_path="fare")
    def fare(self, request, pk=None):
        self.get_object()

        fare_data = get_ride_fare()

        return success_response(
            message="Fare calculated successfully",
            data=fare_data,
            status_code=status.HTTP_200_OK,
        )

class UserActiveRidesView(APIView):
    @swagger_auto_schema(
        operation_summary="Get active rides",
        operation_description="Returns active rides belonging to the authenticated user.",
        responses={
            200: "Active rides retrieved successfully",
            401: "Authentication required",
        },
    )
    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user
        ).filter(
            Q(status__name="REQUESTED") |
            Q(status__name="ACCEPTED") |
            Q(status__name="DRIVER_ARRIVING") |
            Q(status__name="STARTED")
        )

        ride_data = list(
            rides.values(
                "id",
                "pickup_address",
                "drop_address",
                "fare",
                "created_at"
            )
        )

        return Response({
            "count": len(ride_data),
            "rides": ride_data
        })

class CompletedRidesView(APIView):
    @swagger_auto_schema(
        operation_summary="Get completed rides",
        operation_description="Returns completed rides belonging to the authenticated user.",
        responses={
            200: "Completed rides retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user,
            status__name="COMPLETED"
        )

        ride_data = list(
            rides.values(
                "id",
                "pickup_address",
                "drop_address",
                "fare",
                "created_at"
            )
        )

        return Response({
            "count": len(ride_data),
            "rides": ride_data
        })

class CancelledRidesView(APIView):
    @swagger_auto_schema(
        operation_summary="Get cancelled rides",
        operation_description="Returns cancelled rides belonging to the authenticated user.",
        responses={
            200: "Cancelled rides retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user,
            status__name="CANCELLED"
        )

        ride_data = list(
            rides.values(
                "id",
                "pickup_address",
                "drop_address",
                "fare",
                "created_at"
            )
        )

        return Response({
            "count": len(ride_data),
            "rides": ride_data
        })

class RideHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get ride history",
        operation_description=(
            "Returns the authenticated user's ride history. "
            "Supports filtering by date, status, driver and fare range."
        ),
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_QUERY,
                description="Filter rides by date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter rides by ride status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "driver",
                openapi.IN_QUERY,
                description="Filter rides by driver ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "min_fare",
                openapi.IN_QUERY,
                description="Minimum fare",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "max_fare",
                openapi.IN_QUERY,
                description="Maximum fare",
                type=openapi.TYPE_NUMBER,
            ),
        ],
        responses={
            200: "Ride history retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):
        rides = (
            Ride.objects
            .filter(user=request.user)
            .select_related(
                "user",
                "driver",
                "vehicle",
                "status",
            )
            .order_by("-created_at")
        )

        # Filter by date
        date = request.query_params.get("date")

        if date:
            rides = rides.filter(
                created_at__date=date
            )

        # Filter by status
        status_name = request.query_params.get("status")

        if status_name:
            rides = rides.filter(
                status__name__iexact=status_name
            )

        # Filter by driver
        driver_id = request.query_params.get("driver")

        if driver_id:
            rides = rides.filter(
                driver_id=driver_id
            )

        # Filter by minimum fare
        min_fare = request.query_params.get("min_fare")

        if min_fare:
            rides = rides.filter(
                fare__gte=min_fare
            )

        # Filter by maximum fare
        max_fare = request.query_params.get("max_fare")

        if max_fare:
            rides = rides.filter(
                fare__lte=max_fare
            )

        serializer = RideSerializer(
            rides,
            many=True
        )

        ride_data = serializer.data

        return Response({
            "count": len(ride_data),
            "rides": ride_data
        })

class DriverRideHistoryView(APIView):
    @swagger_auto_schema(
        operation_summary="Get driver ride history",
        operation_description="Returns rides assigned to the authenticated driver.",
        responses={
            200: "Driver ride history retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):
        rides = Ride.objects.filter(
            driver__user=request.user
        ).order_by("-created_at")

        ride_data = list(
            rides.values(
                "id",
                "pickup_address",
                "drop_address",
                "fare",
                "status__name",
                "created_at"
            )
        )

        return Response({
            "count": len(ride_data),
            "rides": ride_data
        })

class DailyRideCountView(APIView):
    @swagger_auto_schema(
        operation_summary="Get daily ride count",
        operation_description="Returns the number of rides created by the user for each day.",
        responses={
            200: "Daily ride count retrieved successfully",
            401: "Authentication required",
        },
    )

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

class TotalCompletedRidesView(GenericAPIView):
    @swagger_auto_schema(
        operation_summary="Get total completed rides",
        operation_description="Returns the total number of completed rides for the authenticated user.",
        responses={
            200: "Total completed rides retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):

        total = Ride.objects.filter(
            user=request.user,
            status__name="COMPLETED"
        ).count()

        return Response({
            "total_completed_rides": total
        })

class TotalFareEarnedView(APIView):
    @swagger_auto_schema(
        operation_summary="Get total fare earned",
        operation_description="Returns the total fare earned by the authenticated driver from completed rides.",
        responses={
            200: "Total fare retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):

        result = Ride.objects.filter(
            driver__user=request.user,
            status__name="COMPLETED"
        ).aggregate(
            total_fare=Sum("fare")
        )

        return Response(result)

class RideAggregationsView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get ride aggregations",
        operation_description=(
            "Returns ride statistics including total rides, "
            "completed rides, cancelled rides and fare statistics."
        ),
        responses={
            200: "Ride aggregations retrieved successfully",
            401: "Authentication required",
        },
    )

    def get(self, request):
        rides = Ride.objects.filter(
            user=request.user
        )

        data = rides.aggregate(
            total_rides=Count("id"),
            completed_rides=Count(
                "id",
                filter=Q(
                    status__name__iexact="COMPLETED"
                )
            ),
            cancelled_rides=Count(
                "id",
                filter=Q(
                    status__name__iexact="CANCELLED"
                )
            ),
            total_earnings=Sum("fare"),
            average_fare=Avg("fare"),
            maximum_fare=Max("fare"),
            minimum_fare=Min("fare"),
        )

        return Response({
            "total_rides": data["total_rides"],
            "completed_rides": data["completed_rides"],
            "cancelled_rides": data["cancelled_rides"],
            "total_earnings": data["total_earnings"] or 0,
            "average_fare": data["average_fare"] or 0,
            "maximum_fare": data["maximum_fare"] or 0,
            "minimum_fare": data["minimum_fare"] or 0,
        })

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
    @swagger_auto_schema(
        operation_summary="Filter rides",
        operation_description=(
            "Filters rides using date range, status, driver, "
            "fare range and ordering."
        ),
        manual_parameters=[
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Ride status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "driver_id",
                openapi.IN_QUERY,
                description="Driver ID",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "min_fare",
                openapi.IN_QUERY,
                description="Minimum fare",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "max_fare",
                openapi.IN_QUERY,
                description="Maximum fare",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Ordering: created_at, -created_at, fare or -fare",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: "Filtered rides retrieved successfully",
            401: "Authentication required",
        },
    )

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


class LargeDatasetRideView(ListAPIView):
    @swagger_auto_schema(
        operation_summary="Get paginated rides",
        operation_description=(
            "Returns rides using pagination optimized for large datasets."
        ),
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of rides per page. Maximum 100.",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: "Paginated rides retrieved successfully",
            401: "Authentication required",
        },
    )

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
    @swagger_auto_schema(
        operation_summary="Update driver location",
        operation_description="Creates or updates the authenticated driver's current location.",
        request_body=DriverLocationSerializer,
        responses={
            200: "Driver location updated successfully",
            201: "Driver location created successfully",
            401: "Authentication required",
        },
    )

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
    @swagger_auto_schema(
        operation_summary="Find nearby drivers",
        operation_description=(
            "Returns available drivers near the specified "
            "latitude and longitude within the requested radius."
        ),
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude between -90 and 90",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude between -180 and 180",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "radius",
                openapi.IN_QUERY,
                description="Search radius",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
        ],
        responses={
            200: "Nearby drivers retrieved successfully",
            400: "Invalid latitude, longitude or radius",
            401: "Authentication required",
        },
    )

    def get(self, request):
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        radius = request.GET.get("radius")

        if latitude is None or longitude is None:
            return Response(
                {"error": "latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if radius is None:
            return Response(
                {"error": "radius is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)

        except (TypeError, ValueError):
            return Response(
                {
                    "error": (
                        "latitude, longitude and radius "
                        "must be valid numbers"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if latitude < -90 or latitude > 90:
            return Response(
                {"error": "Invalid latitude"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if longitude < -180 or longitude > 180:
            return Response(
                {"error": "Invalid longitude"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if radius <= 0:
            return Response(
                {"error": "Invalid radius"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nearby_drivers = find_nearby_drivers(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        return Response(
            nearby_drivers,
            status=status.HTTP_200_OK,
        )

class VehicleTypeListView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="List active vehicle types",
        operation_description="Returns all active vehicle types.",
        responses={
            200: VehicleTypeSerializer(many=True),
            401: "Authentication required",
        },
    )

    def get(self, request):
        cache_key = "vehicle_types"

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        vehicle_types = VehicleType.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = VehicleTypeSerializer(
            vehicle_types,
            many=True
        )

        data = serializer.data

        cache.set(
            cache_key,
            data,
            3600
        )

        return Response(data)