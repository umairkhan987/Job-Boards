from django.db import models

from accounts.models import User
from employer.models import PostTask


class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='proposals')
    task = models.ForeignKey(PostTask, on_delete=models.DO_NOTHING, related_name='proposals')
    rate = models.IntegerField(default=0)
    days = models.IntegerField(default=1)
    status = models.CharField(blank=True, null=True, max_length=250)
    rating = models.FloatField(default=0.0)
    onBudget = models.IntegerField(default=0)
    onTime = models.IntegerField(default=0)
    comment = models.TextField(blank=True, null=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task.title + "  " + self.user.email

