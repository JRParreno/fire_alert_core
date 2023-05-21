from typing import Iterable, Optional
from django.db import models
from user_profile.models import UserProfile


class FireAlertServices(models.Model):

    SAMPLE = 'sample'
    TEST = 'test'

    INCIDENT_TYPE_CHOICES = [
        (SAMPLE, 'Sample'),
        (TEST, 'Test'),
    ]

    sender = models.ForeignKey(
        UserProfile, related_name='sender_profille', on_delete=models.CASCADE)
    google_map_url = models.CharField(null=False, blank=False, max_length=100)
    message = models.CharField(null=False, blank=False, max_length=350)
    longitude = models.FloatField(null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    incident_type = models.CharField(
        choices=INCIDENT_TYPE_CHOICES, default=SAMPLE, max_length=100)
    image = models.ImageField(
        upload_to='images/services/', blank=True, null=True)
    video = models.FileField(
        upload_to='videos/services/', blank=True, null=True)
    is_done = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sender.user.email + " " + self.date_created.strftime("%m/%d/%Y, %H:%M:%S")

    # send notification if done
    def save(self, *args, **kwargs) -> None:

        if not self.is_done:
            # SEND NOTIFICATIONS TO USER
            pass

        super(FireAlertServices, self).save(*args, **kwargs)
