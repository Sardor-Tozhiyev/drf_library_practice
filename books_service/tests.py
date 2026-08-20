from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books_service.models import Book

User = get_user_model()


def sample_book(**kwargs):
    defaults = {
        "title": "Clean Code",
        "author": "Robert Martin",
        "cover": Book.CoverChoices.SOFT,
        "inventory": 5,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


class BookAccessTests(APITestCase):
    """Reading is open to any authenticated user, writing is staff-only."""

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass12345")
        self.staff = User.objects.create_user(
            email="staff@test.com", password="pass12345", is_staff=True
        )
        self.book = sample_book()
        self.list_url = reverse("books_service:book-list")

    def test_list_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_books(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "New Book",
            "author": "Someone",
            "cover": Book.CoverChoices.HARD,
            "inventory": 3,
            "daily_fee": "2.00",
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 1)

    def test_staff_can_create_book(self):
        self.client.force_authenticate(self.staff)
        payload = {
            "title": "New Book",
            "author": "Someone",
            "cover": Book.CoverChoices.HARD,
            "inventory": 3,
            "daily_fee": "2.00",
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_regular_user_cannot_delete_book(self):
        self.client.force_authenticate(self.user)
        url = reverse("books_service:book-detail", args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.book.id).exists())
