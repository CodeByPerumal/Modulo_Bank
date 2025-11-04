from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification

User = get_user_model()

class NotificationModelTests(APITestCase):
    def test_notification_creation(self):
        user = User.objects.create_user(username='testuser', password='pass123')
        notification = Notification.objects.create(
            user=user,
            message="Test notification"
        )
        self.assertEqual(str(notification), f"Notification for {user.username}: Test notification")
        self.assertFalse(notification.is_read)


class NotificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass123')
        self.other_user = User.objects.create_user(username='otheruser', password='pass123')

        self.list_url = reverse('notifications-list')

        # Create notifications
        Notification.objects.create(user=self.user, message="User 1 - Notification 1")
        Notification.objects.create(user=self.user, message="User 1 - Notification 2")
        Notification.objects.create(user=self.other_user, message="User 2 - Notification 1")

        # ✅ Authenticate using DRF force_authenticate
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_auth_required(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_view_their_notifications(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for notif in response.data:
            self.assertIn("User 1", notif['message'])

    def test_notifications_are_ordered_desc(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [n['created_at'] for n in response.data]
        self.assertEqual(dates, sorted(dates, reverse=True))
