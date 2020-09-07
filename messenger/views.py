from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from accounts.models import User
from notification.models import MessageNotification
from .forms import MessageForm
from .models import Messages


@login_required
def messages(request):
    try:
        if request.method == "POST" and request.is_ajax():
            form = MessageForm(request.POST)
            if form.is_valid():
                receiver_id = request.POST.get('receiver_id')
                receiver = User.objects.get(pk=receiver_id)
                message = form.save(commit=False)
                message.receiver = receiver
                message.sender = request.user
                message.save()
                current_message = render_to_string("Messenger/include/partial_message.html", {"message": message})
                return JsonResponse({"success": True, "msg": "Message Sent", "current_message": current_message})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({'success': False, 'errors': errors})
        else:
            message_list = get_current_user_msg(request)
            return render(request, 'Messenger/messages.html', {"messages": message_list})
    except Exception as e:
        raise Http404(str(e))


@login_required
def message_details(request, id):
    notifications = MessageNotification.objects.filter(actor_id=id, recipient_id=request.user.id)
    if notifications.exists():
        notifications.update(is_read=True)

    message_list = get_current_user_msg(request)
    receiver = User.objects.get(pk=id)
    full_name = receiver.first_name + " " + receiver.last_name
    message_detail = []
    if receiver:
        message_detail = Messages.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)).order_by(
            'created_at')

    context = {
        "full_name": full_name,
        "messages": message_list,
        "message_details": message_detail,
    }
    return render(request, 'Messenger/messages.html', context)


@login_required
def messages_delete(request):
    try:
        if request.method == "POST" and request.is_ajax():
            id = request.POST.get("receiver_id")
            receiver = User.objects.get(pk=id)
            conversation = Messages.objects.filter(
                Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
            if conversation.exists():
                conversation.delete()
                # TODO: update query and find alternative way to delete messages.
                # conversation.filter(sender=request.user).update(sender=None)
                # conversation.filter(receiver=request.user).update(receiver=None)
                return JsonResponse({"success": True, "msg": "Conversation Deleted.", "url": redirect("messages").url})
            else:
                return JsonResponse({"success": False, "errors": "Conversation not found."})
        else:
            raise Http404("Invalid request")
    except Exception as e:
        raise Http404(str(e))


# TODO: convert this query into django queryset
def get_current_user_msg(request):
    return Messages.objects.raw(
        """
        select id, receiver_id, sender_id, message_content, created_at
        from (  select *, max(created_at)
        over (partition by min(receiver_id, sender_id), max(receiver_id, sender_id)) last_date
        from messenger_messages
        where %s in (receiver_id, sender_id) )
        where created_at = last_date order by id desc
        """, [request.user.id])
