from django.db.models import signals
from django.test import TestCase

from accounts.models import User, Profile
from employer.forms import experience_level
from employer.models import PostTask, skills, Offers
from freelancers.models import Proposal


class TestPostTask(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.task = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="hourly",
        )
        Proposal.objects.create(
            user=self.user2,
            task=self.task,
            rate=40,
            days=2,
        )
        Proposal.objects.create(
            user=self.user2,
            task=self.task,
            rate=30,
            days=2,
        )

    def test_str(self):
        self.assertEqual(self.task.__str__(), "IOS project")

    def test_get_avg_value(self):
        self.assertEqual(self.task.get_avg_value(), 30)

    def test_get_avg_bid(self):
        self.assertEqual(self.task.get_avg_bids(), 35)

    def test_is_hourly_task(self):
        self.assertEqual(self.task.is_hourly_task(), True)

    def test_get_job_status_color(self):
        self.assertEqual(self.task.get_job_status_color(), "yellow")
        self.task.job_status = "Completed"
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.get_job_status_color(), "green")


class TestOffer(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
        )
        self.offer = Offers.objects.create(
            profile=profile,
            full_name="umair khan",
            email="test@email.com",
            offer_message="Hi i need react frontend developer."
        )

    def test_str(self):
        self.assertEqual(self.offer.__str__(), "Hi i need react frontend developer.")