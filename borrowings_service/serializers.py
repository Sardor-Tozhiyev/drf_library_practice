from django.utils import timezone
from rest_framework import serializers

from books_service.serializers import BookSerializer
from borrowings_service.models import Borrowing


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
        book = validated_data["book"]
        book.inventory -= 1
        book.save(update_fields=["inventory"])

        validated_data["user"] = self.context["request"].user
        borrowing = super().create(validated_data)

        from payments_service.models import Payment
        from payments_service.services import create_payment_session
        from django_q.tasks import async_task

        create_payment_session(borrowing, Payment.Type.PAYMENT, self.context["request"])
        async_task("notifications.services.notify_new_borrowing", borrowing.id)

        return borrowing


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

    def save(self):
        self.instance.actual_return_date = timezone.now().date()
        self.instance.book.inventory += 1
        self.instance.book.save(update_fields=["inventory"])
        self.instance.save(update_fields=["actual_return_date"])

        if self.instance.actual_return_date > self.instance.expected_return_date:
            from payments_service.models import Payment
            from payments_service.services import create_payment_session

            create_payment_session(
                self.instance, Payment.Type.FINE, self.context["request"]
            )

        return self.instance
