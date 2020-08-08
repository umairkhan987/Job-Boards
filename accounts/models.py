import os

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

#  We use it because we change default username with email
from django_currentuser.middleware import get_current_user


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email is not empty")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extrafields):
        extrafields.setdefault('is_staff', True)
        extrafields.setdefault('is_superuser', True)
        extrafields.setdefault('is_active', True)

        if extrafields.get('is_staff') is not True:
            raise ValueError("Superuser must have is staff True")
        if extrafields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser True")
        return self.create_user(email, password, **extrafields)


def upload_profile_img(instance, filename):
    return 'Images/Profile/{user}/{filename}'.format(user=instance.id, filename=filename)


def upload_user_cv(instance, filename):
    return 'Files/CV/{user}/{filename}'.format(user=instance.user.id, filename=filename)


class User(AbstractUser):
    is_Freelancer = models.BooleanField(default=False)
    is_Employer = models.BooleanField(default=False)
    profileImg = models.ImageField(upload_to=upload_profile_img, null=True, blank=True)

    # set email instead of username
    username = None
    email = models.EmailField(verbose_name="Email Address", unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def task_completed(self):
        return self.tasks.filter(job_status__exact="Completed").count()

    def task_InProgress(self):
        return self.tasks.filter(job_status__exact="In Progress").count()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name="profile")
    rate = models.IntegerField(default=5)
    skills = models.CharField(blank=True, null=True, max_length=250)
    tags = models.CharField(blank=True, max_length=250)
    country = models.CharField(blank=True, max_length=250)
    introduction = models.TextField(blank=True, max_length=2000)
    userCV = models.FileField(upload_to=upload_user_cv, blank=True, null=True)
    total_hired = models.IntegerField(default=0)
    total_job_done = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def skill_as_list(self):
        return self.skills.split(',')

    def get_file_name(self):
        if self.userCV:
            return os.path.basename(self.userCV.name)
        else:
            return None

    def calculate_success_rate(self):
        if self.total_job_done < 1:
            return 0
        return (self.total_job_done / self.total_hired) * 100

    def calculate_rating(self):
        if self.total_job_done < 1:
            return 0
        return (self.total_job_done / self.total_hired) * 5

    def get_work_history(self):
        return self.user.proposals.filter(status__exact='completed')

    def get_bookmark_profile(self):
        user = get_current_user()
        return user.bookmarks.filter(freelancer_id=self.id).exists()


# create Employer Profile if user Signup as Employer using Signals
@receiver(post_save, sender=User)
def create_freelancer_profile(sender, instance, created, **kwargs):
    if created and instance.is_Freelancer:
        Profile.objects.get_or_create(user=instance)
