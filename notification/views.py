from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .models import MessageNotification, Notification


@login_required
def unread(request):
    notifications = MessageNotification.objects.filter(recipient=request.user).order_by('-timestamp')
    notifications.update(is_seen=True)
    html = render_to_string("Notification/include/partial_message_notification_list.html",
                            {"message_notifications": notifications}, request)
    return JsonResponse({"success": True, "html": html})


@login_required
@csrf_exempt
def mark_all_as_read(request):
    if request.method == "POST" and request.is_ajax():
        request.user.messages.update(is_read=True)
        request.user.msg_notifications.update(is_read=True)
        notifications = request.user.msg_notifications.order_by("-timestamp")
        html = render_to_string("Notification/include/partial_message_notification_list.html",
                                {"message_notifications": notifications}, request)
        return JsonResponse({"success": True, "html": html})
    return HttpResponseBadRequest()


@login_required
def notification_unread(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.update(is_seen=True)
    html = render_to_string("Notification/include/partial_notification_list.html",
                            {"notifications_list": notifications}, request)
    return JsonResponse({"success": True, "html": html})
