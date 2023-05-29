from django.urls import path

from .views import on_going, completed, rejected, edit_report_view
app_name = 'services'

urlpatterns = [
    path('on-going', on_going, name='on_going'),
    path('completed', completed, name='completed'),
    path('rejected', rejected, name='rejected'),
    path('edit-report-view/<pk>', edit_report_view, name='edit_report_view'),
]
