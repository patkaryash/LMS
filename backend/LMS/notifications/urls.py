from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationList.as_view(), name='notification-list'),
    path('read-all/', views.mark_all_notifications_read, name='notification-read-all'),
    path('unread-count/', views.unread_count, name='notification-unread-count'),
    path('send-sms/', views.send_sms_notification, name='notification-send-sms'),
    path('<int:pk>/read/', views.mark_notification_read, name='notification-mark-read'),
]
