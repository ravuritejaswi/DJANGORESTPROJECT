import logging
logger = logging.getLogger(__name__)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from .serializers import ChangePasswordSerializer
from .serializers import LogoutSerializer
from .models import Profile, Notification
from .serializers import ProfileSerializer, NotificationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from core.throttles import LoginThrottle, RegistrationThrottle
from drf_yasg.utils import swagger_auto_schema
from .permissions import IsAdminRole
from rest_framework.pagination import PageNumberPagination


class RegisterAPIView(APIView):
    throttle_classes = [RegistrationThrottle]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Creates a new user account.",
        request_body=RegisterSerializer,
        responses={
            201: "User registered successfully",
            400: "Invalid registration data",
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            logger.info("User registration successful")
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        logger.warning("User registration failed")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    throttle_classes = [LoginThrottle]

    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Authenticates a user and returns JWT access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: "Login successful",
            400: "Invalid email or password",
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            logger.info("User login successful")

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
        logger.warning("User login failed: invalid credentials")

        return Response(
            {"success": False, "message": "Invalid email or password."},
            status=status.HTTP_400_BAD_REQUEST
        )# Create your views here.

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Get user profile",
        operation_description="Returns the authenticated user's basic profile information.",
        responses={
            200: "Profile retrieved successfully",
            401: "Authentication credentials were not provided.",
        },
    )

    def get(self, request):
        return Response({
            "message": "Welcome!",
            "email": request.user.email,
            "username": request.user.username,
        })
    @swagger_auto_schema(
        operation_summary="Create user profile",
        operation_description="Creates a profile for the authenticated user.",
        request_body=ProfileSerializer,
        responses={
            201: ProfileSerializer,
            400: "Invalid profile data",
            401: "Authentication credentials were not provided.",
        },
    )
    def post(self, request):
        serializer = ProfileSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        profile = serializer.save(user=request.user)

        return Response(
            ProfileSerializer(profile).data,
            status=201
        )

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="Changes the password of the authenticated user.",
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password changed successfully",
            400: "Invalid password data",
            401: "Authentication credentials were not provided.",
        },
    )

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
    @swagger_auto_schema(
        operation_summary="User logout",
        operation_description="Logs out the authenticated user using the refresh token.",
        request_body=LogoutSerializer,
        responses={
            200: "Logged out successfully",
            400: "Invalid logout data or refresh token",
            401: "Authentication credentials were not provided.",
        },
    )
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

class ProfileCRUDAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="Create profile",
        operation_description="Creates a profile for the authenticated user.",
        request_body=ProfileSerializer,
        responses={
            201: ProfileSerializer,
            400: "Invalid profile data",
            401: "Authentication credentials were not provided.",
        },
    )
# Create Profile
    def post(self, request):
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, created_by=request.user, updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="View profile",
        operation_description="Returns the authenticated user's profile.",
        responses={
            200: ProfileSerializer,
            401: "Authentication credentials were not provided.",
            404: "Profile not found",
        },
    )
    # View Profile
    def get(self, request):
        profile = get_object_or_404(Profile.objects.select_related("user"), user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Update profile",
        operation_description="Updates the authenticated user's profile.",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: "Invalid profile data",
            401: "Authentication credentials were not provided.",
            404: "Profile not found",
        },

)# Update Profile
    def put(self, request):
        profile = get_object_or_404(Profile.objects.select_related("user"), user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Delete profile",
        operation_description="Soft-deletes the authenticated user's profile.",
        responses={
            204: "Profile deleted successfully",
            401: "Authentication credentials were not provided.",
            404: "Profile not found",
        },
)

    # Delete Profile
    def delete(self, request):
        profile = get_object_or_404(Profile.objects.select_related("user"), user=request.user)
        profile.is_deleted = True
        profile.save()
        return Response(
            {"message": "Profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

@swagger_auto_schema(
    operation_summary="List user profiles",
    operation_description=(
        "Returns profiles for administrators. "
        "Supports filtering, searching, ordering and pagination."
    ),
    responses={
        200: ProfileSerializer(many=True),
        401: "Authentication credentials were not provided.",
        403: "Administrator permission required.",
    },
)
class ProfileListAPIView(ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    queryset = Profile.objects.filter(is_deleted=False)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = ["city", "state", "country", "bio"]

    ordering_fields = ["city", "state", "country"]

    filterset_fields = ["city", "state", "country"]

class RestoreProfileAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Restore profile",
        operation_description="Restores the authenticated user's deleted profile.",
        responses={
            200: "Profile restored successfully",
            401: "Authentication credentials were not provided.",
            404: "Profile not found",
        },
    )
    def post(self, request):
        profile = Profile.objects.select_related("user").get(user=request.user)

        profile.is_deleted = False
        profile.save()

        return Response(
            {"message": "Profile restored successfully"},
            status=status.HTTP_200_OK
        )

class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class NotificationListAPIView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    @swagger_auto_schema(
        operation_summary="List notifications",
        operation_description="Returns notifications belonging to the authenticated user.",
        responses={
            200: NotificationSerializer(many=True),
            401: "Authentication credentials were not provided.",
        },
    )

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Mark notification as read",
        operation_description="Marks a specific notification as read for the authenticated user.",
        responses={
            200: "Notification marked as read",
            401: "Authentication credentials were not provided.",
            404: "Notification not found",
        },
    )

    def patch(self, request, pk):
        notification = get_object_or_404(
            Notification,
            pk=pk,
            user=request.user
        )

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response(
            {
                "message": "Notification marked as read."
            },
            status=status.HTTP_200_OK
        )

class NotificationReadAllAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="Mark all notifications as read",
        operation_description="Marks all unread notifications of the authenticated user as read.",
        responses={
            200: "All notifications marked as read",
            401: "Authentication credentials were not provided.",
        },
        )

    def post(self, request):
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response(
            {
                "message": "All notifications marked as read.",
                "updated_count": updated_count
            },
            status=status.HTTP_200_OK
        )