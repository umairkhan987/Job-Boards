import os
from django.db import models
from django.db.models import Avg
from multiselectfield import MultiSelectField
from accounts.models import User, Profile

# 3rd part package
from django_currentuser.middleware import get_current_user

skills = (
    ('Angular', 'Angular'),
    ('React', 'React'),
    ('Vue', 'Vue'),
    ('CSS', 'CSS'),
    ('Html', 'Html'),
    ('Bootstrap', 'Bootstrap'),
    ('JavaScript', 'JavaScript'),
    ('C#', 'C#'),
    ('C++', 'C++'),
    ('Java', 'Java'),
    ('Python', 'Python'),
    ('Php', 'Php'),
    ('Ruby', 'Ruby'),
    ('Objective-C', 'Objective-C'),
    ('Swift', 'Swift'),
    ('Logo Design', 'Logo Design'),
    ('Game Design', 'Game Design'),
    ('PhotoShop Editing', 'PhotoShop Editing'),
    ('Banner Ads', 'Banner Ads'),
    ('Business Card', 'Business Card'),
)


def upload_project_file(instance, filename):
    return 'Files/Tasks/{task}/{filename}'.format(task=instance.id, filename=filename)


class PostTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="tasks")
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

    def in_progress(self):
        return self.job_status == "In Progress"

    def get_avg_value(self):
        return int((self.min_price + self.max_price) / 2)

    def user_submitted_proposal(self):
        user = get_current_user()
        if not user.is_authenticated:
            return False
        return self.proposals.filter(user=user).exists()

    def get_avg_bids(self):
        avg = self.proposals.all().aggregate(Avg('rate'))['rate__avg']
        return int(avg) if avg is not None else 0

    def get_bookmark_task(self):
        user = get_current_user()
        if not user.is_authenticated:
            return False
        return user.bookmarks.filter(task_id=self.id).exists()

    def is_hourly_task(self):
        if self.project_type == "hourly":
            return True
        return False

    def get_job_status_color(self):
        if self.job_status == "Pending":
            return "yellow"
        elif self.job_status == "Completed":
            return "green"
        else:
            return "blue"


def upload_offer_file(instance, filename):
    return 'Files/Offer/{filename}'.format(filename=filename)


class Offers(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="offers")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_offers')
    offer_message = models.CharField(max_length=500)
    offer_file = models.FileField(upload_to=upload_offer_file, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.offer_message

    def get_full_name(self):
        return self.sender.first_name + " " + self.sender.last_name
