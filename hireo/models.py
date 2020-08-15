import datetime

from django.db import models

from accounts.models import User, Profile
from employer.models import PostTask


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    freelancer_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    task = models.OneToOneField(PostTask, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='senders')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='receivers')
    message_content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message_content

    def get_time_sign(self):
        return self.created_at.date()


# TODO: Change the filename
def upload_offer_file(instance, filename):
    return 'Files/Offer/{filename}'.format(filename=filename)


class Offers(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="offers")
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_offers')
    offer_message = models.CharField(max_length=500)
    offer_file = models.FileField(upload_to=upload_offer_file, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
