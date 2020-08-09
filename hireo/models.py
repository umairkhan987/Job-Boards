from django.db import models

from accounts.models import User, Profile
from employer.models import PostTask


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    # freelancer_id = models.IntegerField(null=True, blank=True)
    freelancer_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    # task_id = models.IntegerField(null=True, blank=True)
    task = models.OneToOneField(PostTask, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
