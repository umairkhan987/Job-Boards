def notifications(request):
    if request.user.is_authenticated:
        message_notifications = request.user.msg_notifications.order_by("-timestamp")
        notifications_list = request.user.notifications.select_related('actor').all()

        return {
            "message_notification_count": message_notifications.filter(is_seen=False).count(),
            'message_notifications': message_notifications,
            "notifications_count": notifications_list.filter(is_seen=False).count(),
            "notifications_list": notifications_list,
        }
    else:
        return dict()
