from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PushToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'username',
            'get_full_name'
        )

        extra_kwargs = {
            'username': {
                'read_only': True
            },
        }


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = (
            'token',
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.get('context', {})
        self.request = context.get('request', None)

        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        ModelClass = self.Meta.model
        token = validated_data['token']
        if not ModelClass.objects.filter(token=token, user=self.request.user):
            # Token can use again
            # ModelClass.objects.filter(
            # user=self.request.user, active=True).update(active=False)
            push_token = ModelClass.objects.create(
                **validated_data, user=self.request.user)
        else:
            raise serializers.ValidationError('Push Token already exists')

        return push_token


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
