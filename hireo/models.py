from datetime import datetime

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

    def get_time_sign(self):
        return self.created_at.date()


