from rest_framework import serializers
from .models import FireAlertServices


class FireAlertServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FireAlertServices
        fields = ['pk', 'sender', 'google_map_url', 'message',
                  'longitude', 'latitude', 'incident_type',
                  'image', 'video', 'is_done', 'address', 'is_rejected'
                  ]
