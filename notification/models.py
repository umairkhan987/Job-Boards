from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from freelancers.models import Proposal
from messenger.models import Messages


class Notifications(models.Model):
    REVIEW_NOTIFICATION = "RN"
    ACCEPT_OFFER = "AO"
    MAKE_OFFER = "MO"
    PLACE_A_BID = "PB"
    TASK_COMPLETED = "TC"

    NOTIFICATION_TYPES = (
        (REVIEW_NOTIFICATION, "rating on your task"),
        (ACCEPT_OFFER, "accept offer"),
        (MAKE_OFFER, "make offer"),
        (PLACE_A_BID, "placed a bid"),
        (TASK_COMPLETED, "complete the task")
    )

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notify_actor")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    action = models.CharField(max_length=2, choices=NOTIFICATION_TYPES)
    is_seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True,
                                            on_delete=models.CASCADE)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    class Meta:
        ordering = ("-timestamp",)


class MessageNotification(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_notify_actor")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_notifications")
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


@receiver(post_save, sender=Proposal)
def create_notification_place_on_bid(sender, instance, created, **kwargs):
    if created:
        notification = Notifications(actor=instance.user, recipient=instance.task.user, target=instance.task,
                                     action=Notifications.PLACE_A_BID)
        notification.save()
