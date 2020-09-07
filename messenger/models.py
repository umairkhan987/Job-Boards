from django.db import models

from accounts.models import User


class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='receivers')
    message_content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message_content
