from rest_framework import serializers
from .models import FireAlertServices


class FireAlertServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = FireAlertServices
        fields = ['pk', 'sender', 'google_map_url', 'message',
                  'longitude', 'latitude', 'incident_type',
                  'image', 'video', 'is_done', 'address', 'is_rejected',
                  'travel_time', 'date_created'
                  ]

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        self.kwargs = context.get("kwargs", None)

        super(FireAlertServiceSerializer, self).__init__(*args, **kwargs)
