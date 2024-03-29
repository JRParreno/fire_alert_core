"""
URL configuration for fire_alert_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import TokenViewWithUserId
from user_profile.views import UserViewSet
from rest_framework.routers import DefaultRouter
from django.conf import settings
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from front_end.views import login_view, home, refresh_home, refresh_queue

schema_view = get_schema_view(
    openapi.Info(
        title="Fire alert hub API",
        default_version='v1',
        description="Testing API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register("user", UserViewSet, basename="user")
router.register('devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api-auth/', include('rest_framework.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('o/login/', TokenViewWithUserId.as_view(), name='token'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('services/', include('front_end.urls', namespace='services')),
    path('login', login_view, name='login'),
    path('', home, name='home'),
    path('refresh-home', refresh_home, name='refresh-home'),
    path('refresh-queue', refresh_queue, name='refresh-queue'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'),
         name='password_reset_complete'),

]
urlpatterns += router.urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
