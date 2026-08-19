from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from books_service.models import Book


class Borrowing(models.Model):
    borrowing_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def clean(self):
        if (
            self.expected_return_date
            and self.expected_return_date < timezone.now().date()
        ):
            raise ValidationError("Expected return date cannot be in the past.")

    def __str__(self):
        return f"{self.book.title} - {self.user.email} ({self.borrowing_date})"

    class Meta:
        ordering = ["-borrowing_date"]


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    payment_type = models.CharField(
        max_length=30,
        choices=TypeChoices.choices,
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.PROTECT, related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
