from rest_framework import viewsets
from .models import DriverProfile
from .serializers import DriverProfileSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = DriverProfile.objects.all()
    serializer_class = DriverProfileSerializer

# Create your views here.
