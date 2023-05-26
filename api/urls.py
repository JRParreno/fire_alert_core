from django.urls import path

from fire_alert_core.views import RegisterView
from user_profile.views import ProfileView
from carousel_image.views import CarouselImageView
from fire_guard.views import FireAlertServicesView
app_name = 'api'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('carousel', CarouselImageView.as_view(), name='carousel'),
    path('fire-guard', FireAlertServicesView.as_view(), name='fire-guard'),
]
