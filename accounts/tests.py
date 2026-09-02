from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .models import User, Profile


class AuthenticationTests(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.register_url = reverse("register")
        self.login_url = reverse("login")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@12345"
        }
        self.user = User.objects.create_user(
            username="authuser",
            email="auth@example.com",
            password="Test@12345"
        )

    def test_user_registration_success(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                email="test@example.com"
            ).exists()
        )

    def test_user_registration_duplicate_email(self):
        User.objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="Test@12345"
        )

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_user_registration_invalid_data(self):
        data = {
            "username": "",
            "email": "invalid-email",
            "password": "123"
        }

        response = self.client.post(
            self.register_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_login_success(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@12345"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "Test@12345"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@12345"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "test@example.com",
                "password": "WrongPassword@123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_logout(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("logout"),
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        refresh_response = self.client.post(
            reverse("token-refresh"),
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            refresh_response.status_code,
        status.HTTP_401_UNAUTHORIZED
        )

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("token-refresh"),
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "access",
            response.data
        )

    def test_password_change(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("change-password"),
            {
                "current_password": "Test@12345",
                "new_password": "NewTest@12345"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("NewTest@12345")
        )

    def test_expired_token(self):
        token = AccessToken.for_user(self.user)

        token.set_exp(
            lifetime=timedelta(seconds=-1)
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(token)}"
        )

        response = self.client.get(
            reverse("profile")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class ProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="Test@12345"
        )

        self.client.force_authenticate(user=self.user)

        self.profile_url = reverse("profile-crud")

        self.profile_data = {
            "phone_number": "9876543210",
            "date_of_birth": "2000-01-15",
            "bio": "Test profile",
            "address": "Hyderabad",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "postal_code": "500001"
        }

    def test_create_profile(self):
        response = self.client.post(
            self.profile_url,
            self.profile_data,
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Profile.objects.filter(
                user=self.user
            ).exists()
        )

    def test_get_profile(self):
        Profile.objects.create(
            user=self.user,
            phone_number="9876543210",
            date_of_birth="2000-01-15",
            bio="Test profile",
            city="Hyderabad"
        )

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["phone_number"],
            "9876543210"
        )

    def test_update_profile(self):
        Profile.objects.create(
            user=self.user,
            phone_number="9876543210",
            date_of_birth="2000-01-15",
            city="Hyderabad"
        )

        response = self.client.put(
            self.profile_url,
            {
                "city": "Warangal"
            },
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["city"],
            "Warangal"
        )

    def test_delete_profile(self):
        Profile.objects.create(
            user=self.user,
            phone_number="9876543210",
            date_of_birth="2000-01-15",
            city="Hyderabad"
        )

        response = self.client.delete(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        profile = Profile.objects.get(user=self.user)

        self.assertTrue(profile.is_deleted)

    def test_profile_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.profile_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_create_profile_invalid_data(self):
        response = self.client.post(
            self.profile_url,
            {
                "phone_number": "",
                "date_of_birth": ""
            },
            format="multipart"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

class PermissionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin_group = Group.objects.create(
            name="Admin"
        )

        self.user_group = Group.objects.create(
            name="User"
        )

        self.driver_group = Group.objects.create(
            name="Driver"
        )

        self.admin = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="Test@12345"
        )

        self.passenger = User.objects.create_user(
            username="passenger",
            email="passenger@example.com",
            password="Test@12345"
        )

        self.driver = User.objects.create_user(
            username="driveruser",
            email="driver@example.com",
            password="Test@12345"
        )

        self.admin.groups.add(self.admin_group)
        self.passenger.groups.add(self.user_group)
        self.driver.groups.add(self.driver_group)

        self.profiles_url = reverse("profiles")

    def test_admin_can_access_profiles(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.profiles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_passenger_cannot_access_profiles(self):
        self.client.force_authenticate(
            user=self.passenger
        )

        response = self.client.get(
            self.profiles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_driver_cannot_access_admin_profiles(self):
        self.client.force_authenticate(
            user=self.driver
        )

        response = self.client.get(
            self.profiles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_anonymous_user_cannot_access_profiles(self):
        response = self.client.get(
            self.profiles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )