from django.urls import path, include
from rest_framework import routers

from books_service.views import BookViewSet

app_name = "books_service"

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
