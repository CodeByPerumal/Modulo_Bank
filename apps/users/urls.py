from django.urls import path
from apps.users.views import RegisterView, CustomTokenObtainPairView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('me/', ProfileView.as_view(), name='profile'),
]
