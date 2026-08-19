from django.core.management.base import BaseCommand
from django.utils import timezone

from borrowings_service.models import Borrowing
from notifications.services import notify_overdue_borrowing


class Command(BaseCommand):
    help = (
        "Finds overdue borrowings and sends Telegram notifications about them"
    )

    def handle(self, *args, **options):
        today = timezone.now().date()

        overdue_borrowings = Borrowing.objects.filter(
            expected_return_date__lt=today,
            actual_return_date__isnull=True,
        )

        count = overdue_borrowings.count()
        for borrowing in overdue_borrowings:
            notify_overdue_borrowing(borrowing.id)

        self.stdout.write(
            self.style.SUCCESS(
                f"Checked overdue borrowings. Notified: {count}"
            )
        )
