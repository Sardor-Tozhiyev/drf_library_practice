from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class Type(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    type = models.CharField(
        max_length=10, choices=Type.choices, default=Type.PAYMENT
    )
    borrowing = models.ForeignKey(
        "borrowings_service.Borrowing",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    session_url = models.URLField(max_length=1024)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"Payment #{self.id} ({self.status}, {self.type}) - ${self.money_to_pay}"
