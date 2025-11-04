# apps/notifications/tests/test_notification_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService

User = get_user_model()


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_create_notification(self):
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test Alert",
            message="This is a test notification."
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, "Test Alert")
        self.assertFalse(notification.is_read)

    def test_get_unread_notifications(self):
        NotificationService.create_notification(self.user, "Alert 1", "Unread message 1")
        NotificationService.create_notification(self.user, "Alert 2", "Unread message 2")

        unread = NotificationService.get_unread_notifications(self.user)
        self.assertEqual(unread.count(), 2)
        self.assertFalse(unread.first().is_read)

    def test_mark_as_read(self):
        notification = NotificationService.create_notification(self.user, "Read Alert", "Mark this as read")
        updated = NotificationService.mark_as_read(notification.id)

        self.assertTrue(updated.is_read)
        self.assertEqual(Notification.objects.filter(is_read=True).count(), 1)

    def test_get_all_notifications(self):
        NotificationService.create_notification(self.user, "A", "Msg A")
        NotificationService.create_notification(self.user, "B", "Msg B")

        all_notifs = NotificationService.get_all_notifications(self.user)
        self.assertEqual(all_notifs.count(), 2)
        self.assertEqual(all_notifs.first().user, self.user)
