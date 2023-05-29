from django.forms import ModelForm
from fire_guard.models import FireAlertServices


class FireAlertServicesForm(ModelForm):
    class Meta:
        model = FireAlertServices
        fields = ['sender', 'address', 'google_map_url',
                  'message', 'longitude', 'latitude', 'incident_type',
                  'is_accepted', 'is_done', 'is_rejected', 'image', 'video'
                  ]

        readonly_fields = ['image', 'video']
