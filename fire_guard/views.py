from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets, permissions, generics, response

from fire_guard.pagination import ExtraSmallResultsSetPagination
from .serializers import FireAlertServiceSerializer
from .models import FireAlertServices
from user_profile.models import UserProfile


class FireAlertServicesView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FireAlertServiceSerializer
    queryset = FireAlertServices.objects.all().order_by('-date_created')
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):

        user_profiles = UserProfile.objects.filter(user=self.request.user.pk)
        if user_profiles.exists():
            user_profile = user_profiles.first()
            return FireAlertServices.objects.filter(sender=user_profile, is_done=False).order_by(
                '-date_created')
