from django.utils import timezone
from rest_framework import serializers

from books_service.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.id", read_only=True)
    user = serializers.CharField(source="user.id", read_only=True)

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
    user = serializers.Charfield(source="user.id", read_only=True)

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

    def validate_book(self, book):
        if book.inventory <= 0:
            raise serializers.ValidationError("This book is currently out of stock.")
        return book

    def create(self, validated_data):
        book = validated_data.pop["book"]
        book.inventory -= 1
        book.save(update_fields=["inventory"])
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
        if self.instance.actual_return_date is None:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )
        return attrs

    def save(self):
        self.instance.actual_return_date = timezone.now().date()
        self.instance.book.inventory += 1
        self.instance.book.save(update_fields=["inventory"])
        self.instance.save(update_fields=["actual_return_date"])
        return self.instance
