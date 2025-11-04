# apps/pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("dashboard/", views.dashboard_page, name="dashboard"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("profile/", views.profile_page, name="profile"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
]
