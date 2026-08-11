from rest_framework.decorators import api_view
from rest_framework.response import Response

from rides.permissions import IsAdminOrDriver

@api_view(['GET'])
def hello(request):
    return Response({
        "message": "Hello Django REST Framework!"
    })

from rest_framework import status
from django.shortcuts import get_object_or_404

from rides.models import DriverProfile
from .serializers import DriverSerializer
from rest_framework import generics
from rides.models import Vehicle
from rides.serializers import VehicleSerializer

class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrDriver]
    filterset_fields = ["vehicle_type", "is_active", "driver"]

    search_fields = [
        "driver__user__username",
        "driver__license_number",
        "vehicle_number",
        "model",
    ]
    ordering_fields = [
        "vehicle_number",
        "model",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminOrDriver]


@api_view(["GET", "POST"])
def drivers(request):

    if request.method == "GET":
        drivers = DriverProfile.objects.all()
        serializer = DriverSerializer(drivers, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = DriverSerializer(data=request.data)

        if serializer.is_valid():
            driver = serializer.save()
            return Response(
                DriverSerializer(driver).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET", "PATCH"])
def driver_detail(request, id):

    driver = get_object_or_404(DriverProfile, id=id)

    if request.method == "GET":
        serializer = DriverSerializer(driver)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = DriverSerializer(
            driver,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            driver = serializer.save()
            return Response(DriverSerializer(driver).data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
