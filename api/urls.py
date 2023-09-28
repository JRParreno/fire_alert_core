from django.urls import path
from django.contrib.auth import views as auth_views

from fire_alert_core.views import RegisterView, ChangePasswordView
from user_profile.views import ProfileView, RequestPasswordResetEmail, UploadIDPhotoView, UploadPhotoView
from carousel_image.views import CarouselImageView
from fire_guard.views import FireAlertServicesView
app_name = 'api'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('forgot-password', RequestPasswordResetEmail.as_view(),
         name='forgot-password '),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
    path('upload-photo/<pk>', UploadPhotoView.as_view(), name='upload-photo'),


    path('upload-id-photo/<pk>', UploadIDPhotoView.as_view(), name='upload-id-photo'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('carousel', CarouselImageView.as_view(), name='carousel'),
    path('fire-guard', FireAlertServicesView.as_view(), name='fire-guard'),
]
