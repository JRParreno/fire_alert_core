from django.urls import path

from fire_alert_core.views import RegisterView


app_name = 'api'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
]
