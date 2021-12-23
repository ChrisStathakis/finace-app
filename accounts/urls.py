from django.urls import path

from .views import register, profile_view

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('profile-view/', profile_view, name='profile_view'),
]