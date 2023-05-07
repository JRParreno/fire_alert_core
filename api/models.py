from django.db import models
from django.contrib.auth.models import User, Group


class PushToken(models.Model):
    active = models.BooleanField(default=True)
    token = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')

    def __str__(self):
        return f'{self.user.email} - {self.token}'

