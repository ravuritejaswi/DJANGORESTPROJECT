from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import LogoutSerializer



class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            return Response(
                {
                    "user": {
                        "email": data["user"].email,
                        "username": data["user"].username,
                    },
                    "access": data["access"],
                    "refresh": data["refresh"],
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )# Create your views here.

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Welcome!",
            "email": request.user.email,
            "username": request.user.username,
        })

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            request.user.set_password(
                serializer.validated_data["new_password"]
            )
            request.user.save()

            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
