from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = Decimal("2.0")


def calculate_payment_amount(borrowing) -> Decimal:
    days = (borrowing.expected_return_date - borrowing.borrowing_date).days
    days = max(days, 1)
    return borrowing.book.daily_fee * days


def calculate_fine_amount(borrowing) -> Decimal:
    overdue_days = (
        borrowing.actual_return_date - borrowing.expected_return_date
    ).days
    overdue_days = max(overdue_days, 0)
    return borrowing.book.daily_fee * overdue_days * FINE_MULTIPLIER


def create_payment_session(borrowing, payment_type: str, request) -> Payment:
    if payment_type == Payment.Type.FINE:
        amount = calculate_fine_amount(borrowing)
    else:
        amount = calculate_payment_amount(borrowing)

    amount_cents = int(amount * 100)

    success_url = (
        request.build_absolute_uri(reverse("payments_service:success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payments_service:cancel"))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{payment_type.title()} for '{borrowing.book.title}'",
                    },
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        status=Payment.Status.PENDING,
        type=payment_type,
        borrowing=borrowing,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        money_to_pay=amount,
    )
    return payment
