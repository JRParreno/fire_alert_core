import json
from django.db import models
from user_profile.models import UserProfile

from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification


class FireAlertServices(models.Model):

    FI = 'FIRE_INCIDENT'
    VA = 'VEHICULAR_ACCIDENT'
    NC = 'NATURAL_CALAMITIES'
    O = "OTHERS"

    INCIDENT_TYPE_CHOICES = [
        (FI, 'Fire Incidents'),
        (VA, 'Vehicular Accidents'),
        (NC, 'Natural Calamities'),
        (O, 'Others'),
    ]

    sender = models.ForeignKey(
        UserProfile, related_name='sender_profille', on_delete=models.CASCADE)
    address = models.CharField(max_length=250,)
    google_map_url = models.CharField(null=True, blank=True, max_length=100)
    message = models.CharField(null=False, blank=False, max_length=350)
    longitude = models.FloatField(null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    incident_type = models.CharField(
        choices=INCIDENT_TYPE_CHOICES, default=O, max_length=100)
    image = models.ImageField(
        upload_to='images/services/', blank=True, null=True)
    video = models.FileField(
        upload_to='videos/services/', blank=True, null=True)
    is_accepted = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    travel_time = models.FloatField(default=0)

    def __str__(self):
        return self.address + " " + self.date_created.strftime("%m/%d/%Y, %H:%M:%S")

    # send notification if done
    def save(self, *args, **kwargs) -> None:
        if not self.is_rejected:
            travel_time = f"{round(self.travel_time, 1)} minutes"
            if self.travel_time > 60:
                travel_time_hrs = round(self.travel_time / 60,
                                        1)
                travel_time = f"{travel_time_hrs} hours"

            body = f"Public Safety Alert\n\nPlease take the appropriate safety measures; there is an emergency at the {self.address}. Fire truck estimated time arrival {travel_time}"
            if self.is_done and self.is_accepted:
                body = f"Public Safety Alert\n\nThe BFP Ligao have successfully accomplished their mission. Thank you for the immediate action."
            if not self.is_done and self.is_accepted:
                body = f"Public Safety Alert\n\nThe BFP Ligao is on the way to your reported location."

            for device in FCMDevice.objects.all().filter(user=self.sender.user):
                data = {
                    "title": "FireGuard",
                    "body": body,
                    "address": self.address,
                    "is_done": self.is_done,
                    "is_rejected": self.is_rejected,
                    "pk": str(self.pk)
                }
                device.send_message(
                    Message(
                        notification=Notification(
                            title=self.incident_type, body=body
                        ),
                        data={
                            "json": json.dumps(data)
                        },
                    )
                )
        else:
            body = "Your report is rejected"
            data = {
                "title": "FireGuard",
                "body": body,
                "address": self.address,
                "is_done": self.is_done,
                "is_rejected": self.is_rejected,
                "pk": str(self.pk)
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
        super(FireAlertServices, self).save(*args, **kwargs)
