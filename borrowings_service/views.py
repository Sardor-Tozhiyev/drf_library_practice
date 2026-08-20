from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from borrowings_service.models import Borrowing
from borrowings_service.serializers import (
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
)


class BorrowingListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        responses=BorrowingListSerializer(many=True),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=BorrowingCreateSerializer,
        responses=BorrowingCreateSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")
        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer
        return BorrowingListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().create(request, *args, **kwargs)


class BorrowingDetailView(generics.RetrieveAPIView):
    serializer_class = BorrowingDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class BorrowingReturnView(generics.UpdateAPIView):
    serializer_class = BorrowingReturnSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["post"]

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book", "user")
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @extend_schema(
        request=None,
        responses=BorrowingReturnSerializer,
    )
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            serializer = self.get_serializer(instance, data={})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
