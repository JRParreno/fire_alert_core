import datetime
import random

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets, permissions, generics, response
from rest_framework.decorators import action
from rest_framework.response import Response
from user_profile.utils import Util
from .models import UserProfile
from .serializers import RegisterSerializer, ProfileSerializer, UploadIDPhotoSerializer, ResetPasswordEmailRequestSerializer
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

from .serializers import ResetPasswordEmailRequestSerializer
from rest_framework import generics, permissions, response, status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.template.loader import get_template
from .email import Util
from base64 import urlsafe_b64encode


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


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_profiles = UserProfile.objects.filter(user=user)

        if user_profiles.exists():
            user_profile = user_profiles.first()

            data = {
                "pk": str(user.pk),
                "profilePk": str(user_profile.pk),
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "address": user_profile.address,
                "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,
                "contactNumber": user_profile.contact_number,
                "isVerified": user_profile.is_verified,
                "otpVerified": user_profile.otp_verified,
                "frontIdPhoto": request.build_absolute_uri(user_profile.front_photo.url) if user_profile.front_photo else None,
                "backIdPhoto": request.build_absolute_uri(user_profile.back_photo.url) if user_profile.back_photo else None,
            }

            return response.Response(data, status=status.HTTP_200_OK)

        else:
            error = {
                "error_message": "Please setup your profile"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        user_details = self.request.data.get('user')
        contact_number = self.request.data.get('contact_number')
        address = self.request.data.get('address')
        user_email = UserProfile.objects.filter(
            user__email=user_details['email']).exclude(user=user).exists()
        check_contact_number = UserProfile.objects.filter(
            contact_number=contact_number).exclude(user=user).exists()

        if user_email:
            error = {
                "error_message": "Email already exists"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)

        if check_contact_number:
            error = {
                "error_message": "Mobile number already exists"
            }
            return response.Response(error, status=status.HTTP_400_BAD_REQUEST)

        user_profile = UserProfile.objects.get(user=user)

        user.email = user_details['email']
        user.first_name = user_details['first_name']
        user.last_name = user_details['last_name']
        user.username = user_details['email']
        user.save()

        user_profile.address = address
        user_profile.contact_number = contact_number
        user_profile.save()

        data = {
            "pk": str(user.pk),
            "profilePk": str(user_profile.pk),
            "username": user.username,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "address": user_profile.address,
            "profilePhoto": request.build_absolute_uri(user_profile.profile_photo.url) if user_profile.profile_photo else None,
            "contactNumber": user_profile.contact_number,
            "isVerified": user_profile.is_verified,
            "otpVerified": user_profile.otp_verified,
            "frontIdPhoto": request.build_absolute_uri(user_profile.front_photo.url) if user_profile.front_photo else None,
            "backIdPhoto": request.build_absolute_uri(user_profile.back_photo.url) if user_profile.back_photo else None,
        }

        return response.Response(data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


class UploadIDPhotoView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UploadIDPhotoSerializer
    queryset = UserProfile.objects.all()


class RequestPasswordResetEmail(generics.CreateAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = []

    def post(self, request):
        email_address = request.data.get('email_address', '')
        check_identity = User.objects.filter(email__exact=email_address)
        if check_identity.exists():
            identity = check_identity.first()
            uidb64 = urlsafe_b64encode(smart_bytes(identity.id))
            token = PasswordResetTokenGenerator().make_token(identity)

            relative_link = reverse(
                'api:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            current_site = get_current_site(
                request=request).domain
            abs_url: str = f"https://{current_site}{relative_link}"

            context_email = {
                "url": abs_url,
                "full_name": f"{identity.first_name} {identity.last_name}"
            }
            message = get_template(
                'forgot_password/index.html').render(context_email)

            context = {
                'email_body': message,
                'to_email': identity.email,
                'email_subject': 'Reset your password'
            }

            Util.send_email(context)
        else:
            return response.Response({'error_message': 'Email not found!'}, status=status.HTTP_404_NOT_FOUND)

        return response.Response(
            {'success': 'We have sent you a link to reset your password'},
            status=status.HTTP_200_OK
        )
