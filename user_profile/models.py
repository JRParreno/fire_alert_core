from django.db import models
from django.contrib.auth.models import User
from fire_alert_core import settings


class UserProfile(models.Model):
    class ProfileManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().select_related('user')

    user = models.OneToOneField(
        User, related_name='profile', on_delete=models.CASCADE)

    address = models.TextField(blank=False, null=False)
    contact_number = models.CharField(max_length=25)
    front_photo = models.ImageField(
        upload_to='front-pictures/', blank=True, null=True)
    back_photo = models.ImageField(
        upload_to='back-pictures/', blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='images/profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.CharField(max_length=2, default=settings.MAX_OTP_TRY)
    otp_max_out = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.last_name} - {self.user.first_name}'
