def notifications(request):
    if request.user.is_authenticated:
        message_notifications = request.user.notifications.order_by("-timestamp")
        return {
            "message_notification_count": message_notifications.filter(is_seen=False).count(),
            'message_notifications': message_notifications
        }
    else:
        return dict()
