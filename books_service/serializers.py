from django.contrib.auth import get_user_model
from rest_framework import serializers

from books_service.models import Book, Borrowing, Payment

User = get_user_model()


class BooksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = (
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee"
        )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id",)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        read_only_fields = ("id")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "status",
            "payment_type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )
