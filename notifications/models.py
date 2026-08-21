from django.db import models


class NotificationLog(models.Model):
    class NotificationType(models.TextChoices):
        NEW_BORROWING = "New borrowing"
        OVERDUE_BORROWING = "Overdue borrowing"
        SUCCESSFUL_PAYMENT = "Successful payment"

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    message_text = models.TextField()
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.notification_type} ({'sent' if self.is_sent else 'failed'})"
