from django.urls import path

from borrowings_service.views import (
    BorrowingDetailView,
    BorrowingListCreateView,
    BorrowingReturnView,
)

app_name = "borrowings_service"

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowing_list_create"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing_detail"),
    path(
        "<int:pk>/return/",
        BorrowingReturnView.as_view(),
        name="borrowing_return",
    ),
]
