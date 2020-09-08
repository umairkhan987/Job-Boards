from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from accounts.models import User
from freelancers.models import Proposal
from messenger.models import Messages
from employer.models import Offers


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
        return None


# create notification when proposal is submitted
@receiver(post_save, sender=Proposal)
def create_notification_place_on_bid(sender, instance, created, **kwargs):
    if created:
        notification = Notification(actor=instance.user, recipient=instance.task.user, target=instance.task,
                                    action=Notification.PLACE_A_BID)
        notification.save()


# create notification when offer is submitted
@receiver(post_save, sender=Offers)
def create_offer_notification_(sender, instance, created, **kwargs):
    if created:
        notification = Notification(actor=instance.sender, recipient=instance.profile.user,
                                    action=Notification.MAKE_OFFER)
        notification.save()


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
