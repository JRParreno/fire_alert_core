from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets, permissions, generics, response
from .serializers import FireAlertServiceSerializer
from .models import FireAlertServices
from user_profile.models import UserProfile


class FireAlertServicesView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FireAlertServiceSerializer
    queryset = FireAlertServices.objects.all().order_by('-date_created')

    def get_queryset(self):
        user_profile = get_object_or_404(
            UserProfile, user=self.request.user.pk)
        return FireAlertServices.objects.filter(sender__exact=user_profile, is_done=False).order_by(
            '-date_created')
