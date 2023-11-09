from django.urls import path

from .views import on_going, completed, rejected, edit_report_view, queue, history_report
app_name = 'services'

urlpatterns = [
    path('on-going', on_going, name='on_going'),
    path('queue', queue, name='queue'),
    path('completed', completed, name='completed'),
    path('rejected', rejected, name='rejected'),
    path('edit-report-view/<pk>', edit_report_view, name='edit_report_view'),
    path('history_report', history_report, name='history_report'),
]
