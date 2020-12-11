from django.db.models import signals
from django.test import TestCase

from accounts.models import User
from employer.forms import experience_level
from employer.models import PostTask, skills
from freelancers.models import Proposal


class TestProposal(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)

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
        self.proposal = Proposal.objects.create(
            user=self.user2,
            task=self.task,
            rate=40,
            days=2,
        )

    def test_str(self):
        self.assertEqual(self.proposal.__str__(), self.task.title)