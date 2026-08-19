from rest_framework import viewsets

from books_service.models import Book
from books_service.permissions import IsAdminOrReadOnly
from books_service.serializers import BookSerializer
from rest_framework import generics, permissions

from books_service.serializers import (
    UserCreateSerializer,
    UserSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
