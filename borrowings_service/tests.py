from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from books_service.models import Book
from borrowings_service.models import Borrowing

User = get_user_model()


def sample_book(**kwargs):
    defaults = {
        "title": "Clean Code",
        "author": "Robert Martin",
        "cover": Book.CoverChoices.SOFT,
        "inventory": 2,
        "daily_fee": Decimal("1.50"),
    }
    defaults.update(kwargs)
    return Book.objects.create(**defaults)


# Payment creation (Stripe) and the notification task are external side
# effects outside the scope of this test suite - they are mocked out.
PATCH_PAYMENT = patch("payments_service.services.create_payment_session")
PATCH_ASYNC_TASK = patch("django_q.tasks.async_task")


class BorrowingCreateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass12345")
        self.book = sample_book(inventory=1)
        self.url = reverse("borrowings_service:borrowing_list_create")
        self.client.force_authenticate(self.user)


    def test_create_borrowing_requires_authentication(self):
        self.client.force_authenticate(None)
        payload = {
            "book": self.book.id,
            "expected_return_date": (timezone.now().date() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass12345")
        self.other_user = User.objects.create_user(email="other@test.com", password="pass12345")
        self.book = sample_book()
        self.own_borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now().date() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        self.other_borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now().date() + timedelta(days=7),
            book=self.book,
            user=self.other_user,
        )
        self.url = reverse("borrowings_service:borrowing_list_create")

    def test_regular_user_sees_only_own_borrowings(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [self.own_borrowing.id])

    def test_staff_can_filter_by_user_id(self):
        staff = User.objects.create_user(
            email="staff@test.com", password="pass12345", is_staff=True
        )
        self.client.force_authenticate(staff)
        response = self.client.get(self.url, {"user_id": self.other_user.id})

        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [self.other_borrowing.id])


class BorrowingReturnTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass12345")
        self.book = sample_book(inventory=1)
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now().date() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )
        self.url = reverse(
            "borrowings_service:borrowing_return", args=[self.borrowing.id]
        )
        self.client.force_authenticate(self.user)

    def test_return_increments_inventory_and_sets_return_date(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.borrowing.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)
        self.assertEqual(self.borrowing.actual_return_date, timezone.now().date())

    def test_cannot_return_twice(self):
        self.client.post(self.url)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BorrowingModelTests(APITestCase):
    def test_clean_rejects_past_expected_return_date(self):
        book = sample_book()
        user = User.objects.create_user(email="user@test.com", password="pass12345")
        borrowing = Borrowing(
            expected_return_date=timezone.now().date() - timedelta(days=1),
            book=book,
            user=user,
        )
        with self.assertRaises(ValidationError):
            borrowing.clean()
