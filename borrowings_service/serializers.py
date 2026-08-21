from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from books_service.models import Book
from books_service.serializers import BookSerializer
from borrowings_service.models import Borrowing
from payments_service.models import Payment
from payments_service.services import create_payment_session


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.IntegerField(source="book.id", read_only=True)
    user = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )

    def validate_expected_return_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Expected return date cannot be in the past."
            )
        return value

    def validate_book(self, book):
        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is currently out of stock."
            )
        return book

    @transaction.atomic
    def create(self, validated_data):
        book = Book.objects.select_for_update().get(
            pk=validated_data["book"].pk
        )

        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is currently out of stock."
            )

        book.inventory -= 1
        book.save(update_fields=["inventory"])

        validated_data["book"] = book
        validated_data["user"] = self.context["request"].user

        return super().create(validated_data)


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "actual_return_date",
        )

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        return_date = timezone.now().date()

        instance.actual_return_date = return_date
        instance.save(update_fields=["actual_return_date"])

        book = Book.objects.select_for_update().get(pk=instance.book_id)
        book.inventory += 1
        book.save(update_fields=["inventory"])

        if return_date > instance.expected_return_date:
            create_payment_session(instance, Payment.Type.FINE, self.context["request"])

        return instance
