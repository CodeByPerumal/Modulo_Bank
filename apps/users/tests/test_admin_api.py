# apps/users/tests/test_admin_api.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()



class AdminUserManagementTests(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.admin_user.is_staff = True
        self.admin_user.role = 'admin'  # ✅ critical line
        self.admin_user.save()

        self.client.force_authenticate(user=self.admin_user)

        # Create a regular customer user
        self.customer_user = User.objects.create_user(
            username='customer1',
            email='cust1@example.com',
            password='custpass',
            role='customer'
        )


    def test_admin_can_view_all_users(self):
        """
        Admin should be able to list all users.
        """
        url = reverse('admin-user-list')  # Make sure this matches your urls.py
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u['username'] == 'customer1' for u in response.data))

    def test_admin_can_change_user_role(self):
        """
        Admin should be able to change a user's role.
        """
        url = reverse('admin-change-user-role', args=[self.customer_user.id])
        response = self.client.put(url, {"role": "auditor"}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer_user.refresh_from_db()
        self.assertEqual(self.customer_user.role, "auditor")

    def test_admin_can_delete_user(self):
        """
        Admin should be able to delete a user.
        """
        url = reverse('admin-delete-user', args=[self.customer_user.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.customer_user.id).exists())
