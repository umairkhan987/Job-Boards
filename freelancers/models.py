from django.db import models

from accounts.models import User
from employer.models import PostTask


class Proposal(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='proposals')
    task = models.ForeignKey(PostTask, on_delete=models.DO_NOTHING, related_name='proposals')
    rate = models.IntegerField(default=0)
    days = models.IntegerField(default=1)
    accept = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    proposal_accept_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.task.title + "  " + self.user.email

