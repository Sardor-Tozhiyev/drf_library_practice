from django.contrib.auth import get_user_model
from rest_framework import serializers

from books_service.models import Book

User = get_user_model()


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("title", "author", "cover", "inventory", "daily_fee")
