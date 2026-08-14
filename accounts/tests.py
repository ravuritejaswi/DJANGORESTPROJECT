
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import User, Profile


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.register_url = reverse("register")
        self.login_url = reverse("login")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@12345"
        }

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