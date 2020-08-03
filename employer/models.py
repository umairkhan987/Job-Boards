import os
from django.db import models
from django.db.models import Avg
from multiselectfield import MultiSelectField
from accounts.models import User

# 3rd part package
from django_currentuser.middleware import get_current_user

skills = (
    ('angular', 'Angular'),
    ('react', 'React'),
    ('vue', 'Vue'),
    ('css', 'CSS'),
    ('html', 'Html'),
    ('bootstrap', 'Bootstrap'),
    ('javaScript', 'JavaScript')
)


def upload_project_file(instance, filename):
    return 'Files/Tasks/{task}/{filename}'.format(task=instance.id, filename=filename)


class PostTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="tasks")
    title = models.CharField(max_length=250)
    skills = MultiSelectField(choices=skills, max_choices=5, min_choices=1)
    tags = models.CharField(max_length=250, blank=True, null=True)
    min_price = models.IntegerField()
    max_price = models.IntegerField()
    exp_level = models.CharField(max_length=50)
    project_type = models.CharField(max_length=50)
    no_of_days = models.IntegerField(default=1, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    task_file = models.FileField(upload_to=upload_project_file, blank=True, null=True)
    job_status = models.CharField(default="Pending", blank=True, null=True, max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def filename(self):
        if self.task_file:
            return os.path.basename(self.task_file.name)
        return None

    def get_avg_value(self):
        return (self.min_price + self.max_price) / 2

    def user_submitted_proposal(self):
        return self.proposals.filter(user=get_current_user()).exists()

    def get_avg_bids(self):
        avg = self.proposals.all().aggregate(Avg('rate'))['rate__avg']
        return avg if avg is not None else 0
