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

        overdue_borrowings = list(
            Borrowing.objects.filter(
                expected_return_date__lt=today,
                actual_return_date__isnull=True,
            ).select_related("user", "book")
        )

        sent = 0
        for borrowing in overdue_borrowings:
            try:
                notify_overdue_borrowing(borrowing.id)
                sent += 1
            except Exception as e: # noqa: BLE001
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to notify for borrowing {borrowing.id}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Checked overdue borrowings. Found: {len(overdue_borrowings)}, "
                f"Notified: {sent}"
            )
        )
