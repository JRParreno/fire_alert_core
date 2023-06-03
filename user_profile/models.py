from django.db import models
from django.contrib.auth.models import User
from fire_alert_core import settings
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification
import json


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
        return str(f'{self.user.last_name} - {self.user.first_name}')

    # send notification if done
    def save(self, *args, **kwargs) -> None:
        if not self.is_verified:
            body = "You are verified!"
            data = {
                "title": "FireGuard",
                "body": body,
            }
            for device in FCMDevice.objects.all().filter(user=self.sender.user):
                device.send_message(
                    Message(
                        notification=Notification(
                            title="FireGuard", body=body
                        ),
                        data={
                            "json": json.dumps(data)
                        }

                    )
                )
        super(UserProfile, self).save(*args, **kwargs)
