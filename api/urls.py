from django.urls import path

from fire_alert_core.views import RegisterView
from user_profile.views import ProfileView


app_name = 'api'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile'),
]
