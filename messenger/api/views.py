from django.db.models import Q
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from messenger.api.serializers import MessageSerializer, MessageDetailSerializer, InboxUserListSerializer
from messenger.models import Messages
from messenger.views import get_current_user_msg
from notification.models import MessageNotification


class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        receiver_id = serializer.validated_data.get("receiver_id", None)
        receiver = get_object_or_404(User, pk=receiver_id)
        serializer.validated_data['receiver'] = receiver
        serializer.validated_data['sender'] = self.request.user
        self.perform_create(serializer)
        Messages.broadcast_msg(sender=self.request.user, receiver=receiver, message=serializer.instance, equal=True)
        return Response(serializer.data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def message_detail_view(request, id, *args, **kwargs):
    notifications = MessageNotification.objects.filter(actor_id=id, recipient_id=request.user.id)
    if notifications.exists():
        notifications.update(is_read=True)

    try:
        receiver = User.objects.get(pk=id)
        if request.user == receiver:
            return Response({"detail": "Forbidden"}, status=403)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=404)

    detail_serializer = None
    if receiver:
        try:
            message_detail = Messages.objects.filter(
                Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)) \
                .exclude(message_not_visible_to=request.user.id) \
                .order_by('created_at')
            message_detail.update(is_read=True)
            detail_serializer = MessageDetailSerializer(message_detail, many=True)
        except Messages.DoesNotExist:
            return Response({"detail": "Messages not found."}, status=404)

    context = {
        "receiver_name": receiver.get_full_name(),
        "profileImg": receiver.get_profile_image_url(),
        "messages": detail_serializer.data,
    }
    return Response(context, status=200)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, ])
def delete_message_view(request, id, *args, **kwargs):
    receiver = User.objects.get(pk=id)
    if request.user == receiver:
        return Response({"detail": "Forbidden"}, status=403)
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
        return Response({"detail": "Deleted"}, status=200)
    else:
        return Response({"detail": "Message not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated, ])
def received_message_view(request, id, *args, **kwargs):
    try:
        msg = get_object_or_404(Messages, pk=id)
        msg.is_read = True
        msg.save()
    except Messages.DoesNotExist:
        return Response({"detail": "Message not found."}, status=404)

    try:
        messageNotification = MessageNotification.objects.get(message_id=msg.id)
        if messageNotification:
            messageNotification.is_read = True
            messageNotification.is_seen = True
            messageNotification.save()
    except Exception as e:
        pass
    message_serializer = MessageDetailSerializer(msg, many=False)
    context = {
        "name": msg.sender.get_full_name(),
        "profileImg": msg.sender.get_profile_image_url(),
        "message": message_serializer.data
    }

    return Response(context, status=200)


class GetUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = InboxUserListSerializer

    def get_queryset(self):
        return get_current_user_msg(self.request)
