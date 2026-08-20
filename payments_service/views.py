import stripe
from django.conf import settings
from django_q.tasks import async_task
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payments_service.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="session_id",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
    )
    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"detail": "Session id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = Payment.objects.filter(
            session_id=session_id,
            borrowing__user=request.user,
        ).first()
        
        if payment is None:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if (
            session.payment_status == "paid"
            and payment.status != Payment.Status.PAID
        ):
            payment.status = Payment.Status.PAID
            payment.save(update_fields=["status"])
            async_task(
                "notifications.services.notify_successful_payment", payment.id
            )
        return Response(
            {
                "detail": (
                    "Payment was successful"
                    if payment.status == Payment.Status.PAID
                    else "Payment is not confirmed yet"
                ),
                "status": payment.status,
            }
        )


class PaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "detail": (
                    "Payment was cancelled. Your payment session is still "
                    "available for 24 hours - you can complete it later "
                    "using the same session_url."
                )
            }
        )
