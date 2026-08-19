from django.contrib.auth.models import AbstractUser
from django.db import models

from borrowings_service.models import Borrowing


class Book(models.Model):

    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        max_length=100,
        choices=CoverChoices.choices,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} by {self.author} - {self.inventory}"

    class Meta:
        ordering = ["title", "inventory"]

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.username


class Borrowing(models.Model):
    borrowing_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrowings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrowings'
    )

    def __str__(self):
        return f"{self.borrowing_date} ({self.book} - {self.user})"

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
        Borrowing,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
