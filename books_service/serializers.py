from rest_framework import serializers

from books_service.models import Borrowing


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
