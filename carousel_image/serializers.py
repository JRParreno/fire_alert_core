from rest_framework import serializers
from .models import CarouselImage


class CarouselImageSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CarouselImage
        fields = ['image', ]

    def __init__(self, *args, **kwargs):
        # init context and request
        context = kwargs.get('context', {})
        self.request = context.get('request', None)
        super(CarouselImageSerializer, self).__init__(*args, **kwargs)

    def get_image(self, data):
        request = self.context.get('request')
        photo_url = data.image.url
        return request.build_absolute_uri(photo_url)
