from django.db import models

from accounts.models import User, Profile
from employer.models import PostTask


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    freelancer_profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    task = models.OneToOneField(PostTask, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class HitCount(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name="views")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip = models.CharField(max_length=40, blank=True, null=True)
    session = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user {self.user} ip={self.ip}"
