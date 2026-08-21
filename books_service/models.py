from django.db import models


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
