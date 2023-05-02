import datetime
import random

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from user_profile.utils import Util
from .models import UserProfile
from .serializers import RegisterSerializer
from django.template.loader import get_template


class UserViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

    def get_queryset(self):                                            # added string
        return super().get_queryset().filter(user=self.request.user.id)

    @action(detail=True, methods=["PATCH"])
    def verify_otp(self, request, pk=None):
        instance = UserProfile.objects.get(user__id=pk)
        if (
            not instance.otp_verified
            and instance.otp == request.data.get("otp")
            and instance.otp_expiry
            and timezone.now() < instance.otp_expiry
        ):
            instance.otp_verified = True
            instance.otp_expiry = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.otp_max_out = None
            instance.save()
            return Response(
                "Successfully verified the user.", status=status.HTTP_200_OK
            )

        return Response(
            "User active or Please enter the correct OTP.",
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["PATCH"])
    def regenerate_otp(self, request, pk=None):
        """
        Regenerate OTP for the given user and send it to the user.
        """
        instance = UserProfile.objects.get(user__id=pk)
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

        context_email = {
            "full_name": f"{instance.user.first_name} {instance.user.last_name}",
            "otp": otp,
        }
        message = get_template('email.html').render(context_email)

        context = {
            'email_body': message,
            'to_email': instance.user.email,
            'email_subject': 'Signup OTP'
        }

        Util.send_email(context)
        # send_otp(instance.phone_number, otp)
        return Response("Successfully generate new OTP.", status=status.HTTP_200_OK)
