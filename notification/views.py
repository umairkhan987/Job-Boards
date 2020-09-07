from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from notification.models import MessageNotification


@login_required
def unread(request):
    notifications = MessageNotification.objects.filter(recipient=request.user).order_by('-timestamp')
    notifications.update(is_seen=True)
    return JsonResponse({"success": True})


@login_required
@csrf_exempt
def mark_all_as_read(request):
    if request.method == "POST" and request.is_ajax():
        request.user.notifications.update(unread=False)
        return JsonResponse({"success": True, "msg": "Successfully printed"})
    return None
