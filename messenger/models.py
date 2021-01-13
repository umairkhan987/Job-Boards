from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django_currentuser.middleware import get_current_user

from accounts.models import User


class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='messages')
    message_content = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # hide message when user delete the message
    message_not_visible_to = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return self.message_content

    def is_sender(self):
        user = get_current_user()
        return True if user == self.sender else False

    @staticmethod
    def broadcast_msg(sender, receiver, message, equal):
        payload = {
            "type": "websocket_receive",
            "message_id": message.id,
            "sender": str(sender),
            "sender_id": sender.id,
            "receiver": str(receiver),
            "Equal": equal,
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(f"{receiver.id}", payload)
        except Exception as e:
            if type(e) == ConnectionRefusedError:
                # print("connection refused")
                return True