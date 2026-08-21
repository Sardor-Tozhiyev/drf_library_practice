from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("users:register")

    def test_register_creates_user_with_hashed_password(self):
        payload = {
            "email": "new@test.com",
            "password": "strongpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email="new@test.com")
        self.assertNotEqual(user.password, "strongpass123")
        self.assertTrue(user.check_password("strongpass123"))

    def test_register_is_staff_field_is_ignored(self):
        payload = {
            "email": "hacker@test.com",
            "password": "strongpass123",
            "is_staff": True,
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="hacker@test.com")
        self.assertFalse(user.is_staff)

    def test_register_duplicate_email_fails(self):
        User.objects.create_user(email="dup@test.com", password="strongpass123")
        response = self.client.post(
            self.register_url, {"email": "dup@test.com", "password": "strongpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserMeEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="me@test.com", password="pass12345")
        self.other = User.objects.create_user(email="other@test.com", password="pass12345")
        self.url = reverse("users:me")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_own_profile_only(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@test.com")

    def test_can_update_own_first_name(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, {"first_name": "Changed"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Changed")


class UserListPermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass12345")
        self.staff = User.objects.create_user(
            email="staff@test.com", password="pass12345", is_staff=True
        )
        self.url = reverse("users:user_list")

    def test_regular_user_cannot_list_users(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_users(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
