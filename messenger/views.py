from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
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
                last_date = request.POST.get("last_message_date", str(datetime.today().date()))
                receiver = User.objects.get(pk=receiver_id)
                message = form.save(commit=False)
                message.receiver = receiver
                message.sender = request.user
                message.save()
                date = datetime.strptime(last_date, "%Y-%m-%d")
                Equal = True
                if datetime.today().date() == date.date():
                    Equal = False

                # send msg to receiver using websocket
                # TODO: send date to broadcast....
                Messages.broadcast_msg(sender=request.user, receiver=receiver, message=message, equal=Equal)

                current_message = render_to_string("Messenger/include/partial_message.html",
                                                   {"message": message, "equal": Equal})
                return JsonResponse({"success": True, "msg": "Message Sent", "current_message": current_message,
                                     "date": datetime.today().date()})
            else:
                errors = {field: str(error[0])[1:-1][1:-1] for (field, error) in form.errors.as_data().items()}
                return JsonResponse({'success': False, 'errors': errors})
        else:
            message_list = get_current_user_msg(request)
            return render(request, 'Messenger/messages.html', {"messages": message_list})
    except Exception as e:
        print(str(e))
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
        last_message = str(message_detail.last().created_at.date())
    context = {
        "full_name": full_name,
        "messages": message_list,
        "message_details": message_detail,
        "last_message_date": last_message
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


@login_required
def received_message(request):
    try:
        if request.method == "GET" and request.is_ajax():
            message_id = request.GET.get("message_id")
            Equal = True if request.GET.get("equal") == 'true' else False
            msg = get_object_or_404(Messages, pk=message_id)
            full_name = msg.sender.first_name + " " + msg.sender.last_name
            received_msg = render_to_string("Messenger/include/partial_received_msg.html",
                                            {"message": msg, "equal": Equal, "full_name": full_name})
            return JsonResponse({"success": True, "received_msg": received_msg})
    except Exception as e:
        raise Http404(str(e))
    return None


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
