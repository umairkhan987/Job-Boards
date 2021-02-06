import os

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

#  We use it because we change default username with email
from django_currentuser.middleware import get_current_user
from multiselectfield import MultiSelectField


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

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_profile_image_url(self):
        if self.profileImg:
            return self.profileImg.url
        else:
            return None

    def task_completed(self):
        if self.is_Freelancer:
            return self.proposals.filter(status__exact="completed").count()
        elif self.is_Employer:
            return self.tasks.filter(job_status__exact="Completed").count()

    def task_InProgress(self):
        if self.is_Freelancer:
            return self.proposals.filter(status__exact="accepted").count()
        elif self.is_Employer:
            return self.tasks.filter(job_status__exact="In Progress").count()

    def task_accepted(self):
        if self.is_Freelancer:
            return self.proposals.filter(status__isnull=False).count()
        return 0


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name="profile")
    # price
    rate = models.IntegerField(default=5)
    skills = MultiSelectField(choices=skills, max_choices=5, min_choices=1)
    tags = models.CharField(blank=True, max_length=250)
    country = models.CharField(blank=True, max_length=250)
    introduction = models.TextField(blank=True, max_length=2000)
    userCV = models.FileField(upload_to=upload_user_cv, blank=True, null=True)
    total_hired = models.IntegerField(default=0)
    total_job_done = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated = models.IntegerField(default=False)
    # calculate success rate
    success_rate = models.IntegerField(default=0)
    rating = models.DecimalField(default=0, max_digits=5, decimal_places=1)

    def __str__(self):
        return self.user.email

    # def skill_as_list(self):
    #     return self.skills.split(',')

    def get_file_name(self):
        if self.userCV:
            return os.path.basename(self.userCV.name)
        else:
            return None

    def calculate_success_rate(self):
        if self.total_job_done < 1:
            return 0
        else:
            total_progress = self.user.proposals.filter(status__iexact="accepted").count()
            total_worked = self.total_hired - total_progress
        return int((self.total_job_done / total_worked) * 100)

    def calculate_rating(self):
        if self.total_job_done < 1:
            return 0
        else:
            total_progress = self.user.proposals.filter(status__iexact="accepted").count()
            total_worked = self.total_hired - total_progress
        return round((self.total_job_done / total_worked) * 5, 1)

    def calculate_onBudget(self):
        completed_job = self.user.proposals.filter(status__iexact="completed")
        if completed_job.exists():
            total_job_completed = completed_job.count()
            total_on_budget = completed_job.filter(onBudget__gt=0).count()
            return (total_on_budget / total_job_completed) * 100
        else:
            return 0

    def calculate_onTime(self):
        completed_job = self.user.proposals.filter(status__iexact="completed")
        if completed_job.exists():
            total_job_completed = completed_job.count()
            total_on_time = completed_job.filter(onTime__gt=0).count()
            return (total_on_time / total_job_completed) * 100
        else:
            return 0

    def get_bookmark_profile(self):
        user = get_current_user()
        if user is None or not user.is_authenticated:
            return False
        return user.bookmarks.filter(freelancer_profile=self).exists()

    def get_rating(self):
        return 0 if self.rating == 0 else self.rating

    # def get_work_history(self):
    #     return self.user.proposals.filter(status__exact='completed')


# Create freelancer profile if user signup as freelancer using Signals
@receiver(post_save, sender=User)
def create_freelancer_profile(sender, instance, created, **kwargs):
    if created and instance.is_Freelancer:
        Profile.objects.get_or_create(user=instance)
