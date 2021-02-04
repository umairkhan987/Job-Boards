from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.db import connection

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
    last_message = None
    if receiver:
        message_detail = Messages.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)) \
            .exclude(message_not_visible_to=request.user.id) \
            .order_by('created_at')

        message_detail.update(is_read=True)
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
                Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)).all()

            if conversation.exists():
                delete_conversation = conversation.filter(
                    ~Q(message_not_visible_to=0) & ~Q(message_not_visible_to=request.user.id))
                if delete_conversation.exists():
                    delete_conversation.delete()

                if conversation.filter(message_not_visible_to=0).exists():
                    conversation = conversation.filter(message_not_visible_to=0).all()
                    conversation.filter(Q(sender=request.user) | Q(receiver=request.user)) \
                        .update(message_not_visible_to=request.user.id)

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

            # get message and read it.
            msg = get_object_or_404(Messages, pk=message_id)
            msg.is_read = True
            msg.save()

            # TODO: change the way to hide notification...
            messageNotification = MessageNotification.objects.get(message=message_id)
            if messageNotification:
                messageNotification.is_read = True
                messageNotification.is_seen = True
                messageNotification.save()

            full_name = msg.sender.first_name + " " + msg.sender.last_name
            received_msg = render_to_string("Messenger/include/partial_received_msg.html",
                                            {"message": msg, "equal": Equal, "full_name": full_name})
            return JsonResponse({"success": True, "received_msg": received_msg, "date": datetime.today().date()})
    except Exception as e:
        raise Http404(str(e))
    return None


@login_required
def get_users_list(request):
    if request.is_ajax():
        path = request.GET.get("path")
        message_list = get_current_user_msg(request)
        users_list = render_to_string("Messenger/include/partial_messages_users_list.html",
                                      {"messages": message_list, "path": path})
        return JsonResponse({"success": True, "users_list": users_list})


# Deprecated
@login_required
def mark_as_read_message(request):
    if request.is_ajax():
        try:
            message_id = request.GET.get("message_id")
            message = Messages.objects.get(id=message_id)
            if message:
                message.is_read = True
                message.save()
                # print("message is read")

            messageNotification = MessageNotification.objects.get(message=message_id)
            if messageNotification:
                messageNotification.delete()
                # print("message notification is deleted")
            return JsonResponse({"success": True})

        except Exception as e:
            print(str(e))
            return JsonResponse({"success": False, "errors": str(e)})


@login_required
def get_users_form_inbox(request):
    if "term" in request.GET:
        keyword = request.GET.get("term")
        message_list = get_current_user_msg(request)
        queryset = [row for row in message_list]
        names = []
        for i in queryset:
            if i.sender == request.user and keyword.lower() in i.receiver.first_name.lower() and i.receiver != request.user:
                obj = {
                    "full_name": i.receiver.first_name + " " + i.receiver.last_name,
                    "id": str(i.receiver.id)
                }
                names.append(obj)
            elif keyword.lower() in i.sender.first_name.lower() and i.sender != request.user:
                obj = {
                    "full_name": i.sender.first_name + " " + i.sender.last_name,
                    "id": str(i.sender.id)
                }
                names.append(obj)
        return JsonResponse(names, safe=False)


# TODO: convert this query into django queryset
def get_current_user_msg(request):
    if connection.vendor == 'sqlite':
        return Messages.objects.raw(
            """
                    select id, receiver_id, sender_id, message_content, created_at
                    from (  select *, max(created_at)
                    over (partition by min(receiver_id, sender_id), max(receiver_id, sender_id)) last_date
                    from messenger_messages
                    where %s in (receiver_id, sender_id) and %s != message_not_visible_to)
                    where created_at = last_date order by id desc
                    """, [request.user.id, request.user.id])
    else:
        return Messages.objects.raw(
            """
            select h.* from messenger_messages h
            where %s in (receiver_id, sender_id) and %s != message_not_visible_to 
            and not exists (
            select 1 from messenger_messages
            where LEAST(receiver_id, sender_id) = LEAST(h.receiver_id, h.sender_id)
                and GREATEST(receiver_id, sender_id) = GREATEST(h.receiver_id, h.sender_id)
            and created_at > h.created_at
            )  
            order by h.id desc
            """, [request.user.id, request.user.id])
