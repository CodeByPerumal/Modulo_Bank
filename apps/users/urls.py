from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    RegisterView,
    CustomTokenObtainPairView,
    ProfileView,
    AdminUserListView,
    AdminChangeUserRoleView,
    ListUsersView,
    ChangeUserRoleView,
    DeleteUserView,
)

urlpatterns = [
    # 🔐 Authentication
    path('register/', RegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 👤 Profile
    path('profile/', ProfileView.as_view(), name='user-profile'),

    # 👮 Admin Endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/change-role/<int:id>/', AdminChangeUserRoleView.as_view(), name='admin-change-role'),

    # 🧰 General Management
    path('users/', ListUsersView.as_view(), name='list-users'),
    path('users/<int:user_id>/delete/', DeleteUserView.as_view(), name='delete-user'),
    path('users/<int:user_id>/role/', ChangeUserRoleView.as_view(), name='change-user-role'),

     # ✅ Admin endpoints
    path('admin/users/', ListUsersView.as_view(), name='admin-user-list'),
    path('admin/users/<int:user_id>/role/', ChangeUserRoleView.as_view(), name='admin-change-user-role'),
    path('admin/users/<int:user_id>/delete/', DeleteUserView.as_view(), name='admin-delete-user'),
]
