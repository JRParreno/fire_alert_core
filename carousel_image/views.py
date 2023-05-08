from django.shortcuts import render
from rest_framework import status, viewsets, permissions, generics, response

from carousel_image.paginate import ExtraSmallResultsSetPagination
from .serializers import CarouselImageSerializer
from .models import CarouselImage


class CarouselImageView(generics.ListAPIView):
    serializer_class = CarouselImageSerializer
    queryset = CarouselImage.objects.all().order_by('-date_updated')
    permission_classes = []
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        return CarouselImage.objects.all().order_by('-date_updated')[:5]
