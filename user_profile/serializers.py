from rest_framework import serializers
from django.contrib.auth.models import User
import base64

from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
import random
from django.conf import settings


class RegisterSerializer(serializers.ModelSerializer):
    # set all fields required and model
    contact_number = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'confirm_password', 'contact_number', 'address',
        ]

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate(self, data):
        password = data['password']
        confirm_password = data['confirm_password']
        email_address = data['email']

        if password != confirm_password:
            raise serializers.ValidationError(
                {"error_message": "Passwords do not match"})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
