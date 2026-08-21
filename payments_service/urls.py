from django.urls import path

from .views import PaymentCancelView, PaymentSuccessView

app_name = "payments_service"

urlpatterns = [
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("cancel/", PaymentCancelView.as_view(), name="cancel"),
]
