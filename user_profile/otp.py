import datetime
import random

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import Util


def verify_otp(self, request, pk=None):
    instance = self.get_object()
    if (
        not instance.is_active
        and instance.otp == request.data.get("otp")
        and instance.otp_expiry
        and timezone.now() < instance.otp_expiry
    ):
        instance.is_active = True
        instance.otp_expiry = None
        instance.max_otp_try = settings.MAX_OTP_TRY
        instance.otp_max_out = None
        instance.save()

        return True

    return False


def regenerate_otp(self, request, pk=None):
    """
    Regenerate OTP for the given user and send it to the user.
    """
    instance = self.get_object()
    if int(instance.max_otp_try) == 0 and timezone.now() < instance.otp_max_out:
        return Response(
            "Max OTP try reached, try after an hour",
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp = random.randint(1000, 9999)
    otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
    max_otp_try = int(instance.max_otp_try) - 1

    instance.otp = otp
    instance.otp_expiry = otp_expiry
    instance.max_otp_try = max_otp_try
    if max_otp_try == 0:
        # Set cool down time
        otp_max_out = timezone.now() + datetime.timedelta(hours=1)
        instance.otp_max_out = otp_max_out
    elif max_otp_try == -1:
        instance.max_otp_try = settings.MAX_OTP_TRY
    else:
        instance.otp_max_out = None
        instance.max_otp_try = max_otp_try
    instance.save()
    Util.send_email(instance.phone_number)
    return "Successfully generate otp"
