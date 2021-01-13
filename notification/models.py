from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse

from accounts.models import User
from freelancers.models import Proposal
from messenger.models import Messages
from employer.models import Offers, PostTask


class MessageNotification(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_notify_actor")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_notifications")
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500, null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    message = models.ForeignKey(Messages, on_delete=models.CASCADE, default=1)

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
                                           text=instance.message_content, message=instance)
        notification.save()


class Notification(models.Model):
    POST_REVIEW = "PR"
    ACCEPT_OFFER = "AO"
    MAKE_OFFER = "MO"
    PLACE_A_BID = "PB"
    TASK_COMPLETED = "TC"
    TASK_CANCELLED = "CT"

    NOTIFICATION_TYPES = (
        (POST_REVIEW, "left you a rating on"),
        (ACCEPT_OFFER, "accepted your proposal on"),
        (MAKE_OFFER, "send offer to you."),
        (PLACE_A_BID, "placed a bid on your"),
        (TASK_COMPLETED, "completed the"),
        (TASK_CANCELLED, "cancelled the"),
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

    def __str__(self):
        return f"{self.id} {self.action}"

    def get_icon(self):
        """ Model method to return specific notification icon. """
        if self.action == Notification.PLACE_A_BID:
            return "icon-material-outline-gavel"
        if self.action == Notification.ACCEPT_OFFER:
            return "icon-material-outline-check"
        if self.action == Notification.TASK_COMPLETED:
            return "icon-material-outline-check-circle"
        if self.action == Notification.TASK_CANCELLED:
            return "icon-material-outline-highlight-off"
        if self.action == Notification.POST_REVIEW:
            return "icon-material-outline-rate-review"
        if self.action == Notification.MAKE_OFFER:
            return "icon-line-awesome-envelope"

    def get_actor_full_name(self):
        """ Get actor full name """
        return f"{self.actor.first_name} {self.actor.last_name}"

    def get_absolute_url(self):
        if self.action == Notification.PLACE_A_BID or self.action == Notification.TASK_COMPLETED or \
                self.action == Notification.TASK_CANCELLED:
            return reverse('manage_proposal', args=[self.target_object_id])
        if self.action == Notification.ACCEPT_OFFER:
            return reverse('my_proposals')
        if self.action == Notification.MAKE_OFFER:
            return reverse("offers")
        if self.action == Notification.POST_REVIEW:
            return reverse("freelancer_reviews")
        return None

    def compare_action(self):
        """ compare action to hide the target object on template """
        if self.action == Notification.MAKE_OFFER:
            return False
        return True


# create notification when proposal is submitted
@receiver(post_save, sender=Proposal)
def create_notification_place_on_bid(sender, instance, created, **kwargs):
    if created:
        notification = Notification(actor=instance.user, recipient=instance.task.user, target=instance.task,
                                    action=Notification.PLACE_A_BID)
        notification.save()


# create offer notification
@receiver(post_save, sender=Offers)
def create_offer_notification(sender, instance, created, **kwargs):
    if created:
        try:
            old_notification = Notification.objects.filter(recipient=instance.profile.user).first()
            if old_notification and (
                    old_notification.actor == instance.sender and
                    old_notification.recipient == instance.profile.user and
                    old_notification.action == Notification.MAKE_OFFER):
                old_notification.delete()

            notification = Notification(actor=instance.sender, recipient=instance.profile.user, target=instance,
                                        action=Notification.MAKE_OFFER)
            notification.save()
        except Exception as e:
            print(str(e))


def notification_handler(actor, recipient, action, **kwargs):
    """
        Handler function to create a Notification instance.
        :requires:
        :param actor: User instance of that user who makes the action.
        :param recipient: User instance, who should be notified.
        :param action: Notification attribute with the right choice from the list.

        :optional:
        :param target: Model instance on which the verb was executed.
    """

    Notification.objects.create(
        actor=actor,
        recipient=recipient,
        action=action,
        target=kwargs.pop("target", None)
    )


# delete offer notifications
@receiver(post_delete, sender=Offers)
@receiver(post_delete, sender=Proposal)
@receiver(post_delete, sender=PostTask)
def delete_offer_notification(sender, instance, **kwargs):
    try:
        if sender.__name__ == Proposal.__name__:
            notification = Notification.objects.filter(target_object_id=instance.task.id, actor=instance.user).first()
            if notification:
                notification.delete()
        else:
            Notification.objects.filter(target_object_id=instance.id).delete()

    except Exception as e:
        print(str(e))


# call the websocket when notification is created.
@receiver(post_save, sender=Notification)
def notification_broadcast(sender, instance, created, **kwargs):
    if created:
        payload = {
            "type": "websocket_receive",
            "key": "user_notification",
        }

        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notifications", payload)
        except Exception as e:
            if type(e) == ConnectionRefusedError:
                # print("connection refused")
                return True


@receiver(post_save, sender=MessageNotification)
def message_notification_broadcast(sender, instance, created, **kwargs):
    if created:
        # print("message notification created")
        payload = {
            "type": "websocket_receive",
            "key": "msg_notification",
        }
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("notifications", payload)
        except Exception as e:
            if type(e) == ConnectionRefusedError:
                # print("connection refused")
                return True
