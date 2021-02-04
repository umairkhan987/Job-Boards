from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from freelancers.api.serializers import NotificationSerializer
from notification.api.serializers import MessageNotificationSerializer
from notification.models import MessageNotification, Notification


class ReadMessageNotificationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = MessageNotificationSerializer

    def get_queryset(self):
        notifications = MessageNotification.objects.filter(recipient=self.request.user).select_related('actor'). \
            order_by('-timestamp')
        notifications.update(is_seen=True)
        return notifications


class MarkAllAsReadView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = MessageNotificationSerializer

    def get_queryset(self):
        user = self.request.user
        user.messages.update(is_read=True)
        user.msg_notifications.update(is_read=True)
        notifications = user.msg_notifications.order_by("-timestamp")
        return notifications


class ReadUserNotificationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        notifications = Notification.objects.filter(recipient=self.request.user).select_related('actor')
        notifications.update(is_seen=True)
        return notifications