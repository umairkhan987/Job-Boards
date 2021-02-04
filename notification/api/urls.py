from django.urls import path
from . import views

urlpatterns = [
    path("message_notification/read/", views.ReadMessageNotificationsView.as_view(),
         name="read_message_notifications_view"),
    path("mark_all_as_read/", views.MarkAllAsReadView.as_view(), name="mark_all_as_read_view"),
    path("notifications/read/", views.ReadUserNotificationsView.as_view(), name="read_user_notifications_view"),
]
