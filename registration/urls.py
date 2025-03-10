# EMS/urls.py
from django.contrib import admin
from django.urls import path
from registration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.registration_view, name='register'),
]