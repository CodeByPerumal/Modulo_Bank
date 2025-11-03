from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User


class UserRegistrationTests(APITestCase):
    def test_register_user_success(self):
        url = reverse('user-register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Testpass123",
            "password2": "Testpass123",
            "phone": "9876543210"
        }

        response = self.client.post(url, data, format='json')
        print("Response data:", response.data)  # 👈 Add this line for debugging
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="StrongPass123"
        )

    def test_login_success(self):
        url = reverse('token_obtain_pair')  # JWT login endpoint
        data = {
            "username": "loginuser",
            "password": "StrongPass123"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
