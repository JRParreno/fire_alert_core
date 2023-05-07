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
from oauth2_provider.models import (
    Application,
    RefreshToken,
    AccessToken
)
from django.utils.crypto import get_random_string
from datetime import (
    datetime,
    timedelta
)


class UserViewSet(viewsets.ModelViewSet):
    """
    UserModel View.
    """

    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

    def get_queryset(self):                                            # added string
        return super().get_queryset().filter(user=self.request.user.id)

    def create_access_token(self, user):
        application = Application.objects.all()

        if application.exists():
            self.expire_seconds = settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
            scopes = settings.OAUTH2_PROVIDER['SCOPES']
            expires = datetime.now() + timedelta(seconds=self.expire_seconds)
            token = get_random_string(32)
            refresh_token = get_random_string(32)

            access_token = AccessToken.objects.create(
                user=user,
                expires=expires,
                scope=scopes,
                token=token,
                application=application.first(),
            )

            refresh_token = RefreshToken.objects.create(
                user=user,
                access_token=access_token,
                token=refresh_token,
                application=application.first(),
            )

            return access_token, refresh_token

        return None

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

            oauth_token, refresh_token = self.create_access_token(
                instance.user)

            data = {
                "access_token": oauth_token.token,
                "expires": self.expire_seconds,
                "token_type": "Bearer",
                "scope": oauth_token.scope,
                "refresh_token": refresh_token.token
            }
            return Response(
                data, status=status.HTTP_200_OK
            )

        error = {
            "error_message": "Please enter the correct OTP."
        }
        return Response(
            error,
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
        otp_expiry = timezone.now() + timedelta(minutes=5)
        max_otp_try = int(instance.max_otp_try) - 1

        instance.otp = otp
        instance.otp_expiry = otp_expiry
        instance.max_otp_try = max_otp_try
        if max_otp_try == 0:
            # Set cool down time
            otp_max_out = timezone.now() + timedelta(hours=1)
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
