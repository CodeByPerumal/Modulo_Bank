from rest_framework import generics, permissions
from apps.users.serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

# ✅ Import all serializers used in this file
from apps.users.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileUpdateSerializer,
    AdminUserRoleUpdateSerializer,
    UserListSerializer  # ✅ add this line
)

# ✅ Import any custom permissions if used
from apps.users.permissions import IsAdmin, IsCustomer



User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
            "date_joined": user.date_joined
        }
        return Response(data)
    

from .permissions import IsAdmin, IsCustomer
from .serializers import UserProfileUpdateSerializer, AdminUserRoleUpdateSerializer

# ✅ Customer: Update their own profile
class UpdateUserProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def get_object(self):
        return self.request.user


# ✅ Admin: List all users
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


# ✅ Admin: Change user role
class AdminChangeUserRoleView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserRoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    lookup_field = 'id'

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser

class ChangeUserRoleView(APIView):
    """
    Admin can change the role of any user.
    """
    permission_classes = [IsAdminUser]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get("role")
        if new_role not in ["customer", "admin", "auditor"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        user.role = new_role
        user.save()
        return Response({"role": user.role}, status=status.HTTP_200_OK)


class ListUsersView(generics.ListAPIView):
    """
    Only admin can view all users.
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class DeleteUserView(APIView):
    """
    Admin can delete a user by ID.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from apps.users.serializers import UserListSerializer
class ListUsersView(generics.ListAPIView):
    """
    Only admin can view all users.
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

