from django.urls import path

from notification import views

urlpatterns = [
    path("unread/", views.read_msg_notifications, name="unread"),
    path('mark-all-as-read/', views.mark_all_as_read, name="mark-all-as-read"),
    path("notify_unread/", views.read_user_notifications, name="notification-unread"),
]
