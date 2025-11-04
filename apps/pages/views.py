# apps/pages/views.py
from django.shortcuts import render

def home_page(request):
    return render(request, "home.html")

def dashboard_page(request):
    return render(request, "dashboard.html")

def login_page(request):
    return render(request, "users/login.html")

def register_page(request):
    return render(request, "users/register.html")

def profile_page(request):
    return render(request, "users/profile.html")

def about_page(request):
    return render(request, "about.html")

def contact_page(request):
    return render(request, "contact.html")
