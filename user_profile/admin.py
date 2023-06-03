from django.contrib import admin
from django.contrib import admin
from .models import UserProfile
from django.core.mail import send_mail
from fire_alert_core import settings


@admin.register(UserProfile)
class UserProfileAdminView(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name',)
    list_filter = ('is_verified',)

    def save_model(self, request, obj, form, change):
        prev_profile = UserProfile.objects.get(pk=obj.pk)
        if obj.is_verified and not prev_profile.is_verified:
            send_mail(
                subject=f'Account Verification',
                message=f'Your FireGuard application account was approved by our team. '
                'Kindly ignore this message if you did not initiate this request.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[obj.user.email],
                html_message=f'Your FireGuard application account was approved by our team. '
                             'Kindly ignore this message if you did not initiate this request.',
            )
            obj.is_verified = True

        super(UserProfileAdminView, self).save_model(
            request, obj, form, change)
