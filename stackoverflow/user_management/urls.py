from django.contrib import admin
from django.urls import path, include
from user_management.views import register_user

app_name = "user_management"


urlpatterns = [
    path("signup/", register_user, name="user_signup"),
]
