from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from hireo.models import Messages


class MessageNotification(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notify_actor")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500, blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.text


@receiver(post_save, sender=Messages)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        # delete old notification of same user
        old_notification = MessageNotification.objects.filter(actor=instance.sender, recipient=instance.receiver)
        if old_notification:
            old_notification.delete()

        notification = MessageNotification(actor=instance.sender, recipient=instance.receiver,
                                           text=instance.message_content)
        notification.save()
