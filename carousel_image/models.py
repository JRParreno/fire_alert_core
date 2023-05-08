from django.db import models
from django.contrib.auth.models import User


class CarouselImage(models.Model):

    image = models.ImageField(
        upload_to='carousel-pictures/',)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
