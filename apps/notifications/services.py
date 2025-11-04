# apps/notifications/services.py
from django.utils import timezone
from apps.notifications.models import Notification

class NotificationService:
    """
    Handles creation and management of user notifications.
    """

    @staticmethod
    def create_notification(user, title, message):
        """
        Create and save a notification for a user.
        """
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            created_at=timezone.now()
        )

    @staticmethod
    def mark_as_read(notification_id):
        """
        Mark a specific notification as read.
        """
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return notification
        except Notification.DoesNotExist:
            return None

    @staticmethod
    def get_unread_notifications(user):
        """
        Return all unread notifications for a user.
        """
        return Notification.objects.filter(user=user, is_read=False).order_by('-created_at')

    @staticmethod
    def get_all_notifications(user):
        """
        Return all notifications for a user.
        """
        return Notification.objects.filter(user=user).order_by('-created_at')
