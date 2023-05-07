import json
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.models import get_access_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.views.base import TokenView
from user_profile.serializers import RegisterSerializer
from user_profile.models import UserProfile
from rest_framework import generics, permissions, response, status
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.response import Response
from django.template.loader import get_template
import re
from oauth2_provider.models import (
    Application,
    RefreshToken,
    AccessToken
)
from datetime import (
    datetime,
    timedelta
)
from django.utils.crypto import get_random_string
import random
from django.conf import settings

from user_profile.models import UserProfile
from user_profile.utils import Util
from fire_alert_core import settings
from api.serializers import ChangePasswordSerializer


class TokenViewWithUserId(TokenView):
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)
        print(body)

        if status == 200:
            body = json.loads(body)
            access_token = body.get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(
                    token=access_token)
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
                body['id'] = str(token.user.id)
                body = json.dumps(body)
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


class RegisterView(generics.CreateAPIView):
    permission_classes = []
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

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

    def post(self, request, *args, **kwargs):
        password = request.data.get('password')
        address = request.data.get('address')
        confirm_password = request.data.get('confirm_password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        mobile_number = request.data.get('contact_number')

        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            data = {
                "error_message": "Email already exists"
            }
            return response.Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=email).exists():
            data = {
                "error_message": "Mobile number already exists"
            }
            return response.Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != confirm_password:
            data = {
                "error_message": "Password does not match"
            }
            return response.Response(
                data=data,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            username=email, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()

        otp_expiry = datetime.now() + timedelta(minutes=10)
        otp = random.randint(1000, 9999)

        UserProfile.objects.create(user=user,
                                   address=address,
                                   contact_number=mobile_number,
                                   otp=otp,
                                   otp_expiry=otp_expiry,
                                   max_otp_try=settings.MAX_OTP_TRY,
                                   )

        context_email = {
            "full_name": f"{user.first_name} {user.last_name}",
            "otp": otp,
        }
        message = get_template('email.html').render(context_email)

        context = {
            'email_body': message,
            'to_email': user.email,
            'email_subject': 'Signup OTP'
        }

        Util.send_email(context)

        data = {
            "id": user.pk,
        }

        return response.Response(
            data=data,
            status=status.HTTP_200_OK
        )


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"error_message": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
            new_password_entry = serializer.data.get("new_password")
            reg = "[^\w\d]*(([0-9]+.*[A-Za-z]+.*)|[A-Za-z]+.*([0-9]+.*))"
            pat = re.compile(reg)

            if 8 <= len(new_password_entry) <= 16:
                password_validation = re.search(pat, new_password_entry)
                if password_validation:
                    self.object.set_password(
                        serializer.data.get("new_password"))
                else:
                    return Response({"error_message":
                                     "Password must contain a combination of letters "
                                     "and numbers "},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error_message": [
                    "Password must contain at least 8 to 16 characters"]},
                    status=status.HTTP_400_BAD_REQUEST)

            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def home(request):
    return render(request, 'home.html',)


def about(request):

    return render(request, 'about.html',)


def contact(request):

    return render(request, 'contact.html',)


def help(request):

    return render(request, 'help.html',)


def term_condition(request):

    return render(request, 'terms-and-conditions.html',)


def privacy_policy(request):

    return render(request, 'privacy-policy.html',)
