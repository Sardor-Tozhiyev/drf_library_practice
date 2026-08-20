import logging

from django.utils import timezone

from .models import NotificationLog
from .telegram import send_telegram_message

logger = logging.getLogger(__name__)


def _log_and_send(notification_type: str, text: str) -> None:
    is_sent = send_telegram_message(text)
    NotificationLog.objects.create(
        notification_type=notification_type,
        message_text=text,
        is_sent=is_sent,
    )


def notify_new_borrowing(borrowing_id: int) -> None:
    from borrowings_service.models import Borrowing

    try:
        borrowing = Borrowing.objects.select_related("book", "user").get(
            id=borrowing_id
        )
    except Borrowing.DoesNotExist:
        logger.error("Borrowing %s not found for notification", borrowing_id)
        return

    text = (
        "📚 <b>Нове бронювання</b>\n"
        f"Книга: {borrowing.book.title}\n"
        f"Користувач: {borrowing.user.email}\n"
        f"Дата видачі: {borrowing.borrowing_date}\n"
        f"Очікувана дата повернення: {borrowing.expected_return_date}"
    )
    _log_and_send(NotificationLog.NotificationType.NEW_BORROWING, text)


def notify_overdue_borrowing(borrowing_id: int) -> None:
    from borrowings_service.models import Borrowing

    try:
        borrowing = Borrowing.objects.select_related("book", "user").get(
            id=borrowing_id
        )
    except Borrowing.DoesNotExist:
        logger.error("Borrowing %s not found for notification", borrowing_id)
        return

    days_overdue = (
        timezone.now().date() - borrowing.expected_return_date
    ).days
    text = (
        "⚠️ <b>Прострочене повернення</b>\n"
        f"Книга: {borrowing.book.title}\n"
        f"Користувач: {borrowing.user.email}\n"
        f"Мало бути повернено: {borrowing.expected_return_date}\n"
        f"Прострочено на {days_overdue} дн."
    )
    _log_and_send(NotificationLog.NotificationType.OVERDUE_BORROWING, text)


def notify_successful_payment(payment_id: int) -> None:
    from payments_service.models import Payment

    try:
        payment = Payment.objects.select_related(
            "borrowing__book", "borrowing__user"
        ).get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error("Payment %s not found for notification", payment_id)
        return

    text = (
        "✅ <b>Оплата успішна</b>\n"
        f"Тип: {payment.get_type_display()}\n"
        f"Книга: {payment.borrowing.book.title}\n"
        f"Користувач: {payment.borrowing.user.email}\n"
        f"Сума: ${payment.money_to_pay}"
    )
    _log_and_send(NotificationLog.NotificationType.SUCCESSFUL_PAYMENT, text)
