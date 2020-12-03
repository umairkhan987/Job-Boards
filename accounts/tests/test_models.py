from django.test import TestCase
from django.db.models import signals

from accounts.models import User, Profile
from employer.models import PostTask
from freelancers.models import Proposal
from hireo.models import Bookmark


class TestUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="12345")

    def test_user_email(self):
        self.assertEqual(self.user.__str__(), "test@email.com")


class TestUserProfile(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="12345")
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
            # userCV=SimpleUploadedFile("test.txt", b"this is a simple test file.")
        )
        self.user2 = User.objects.create_user(email="test2@email.com", password='12345')
        self.task = PostTask.objects.create(
            user=self.user2,
            title="python Script",
            skills=['python', ],
            min_price=50,
            max_price=100,
            exp_level="beginner",
            project_type="fixed",
        )

    def test_user_email(self):
        self.assertEqual(self.profile.__str__(), self.user.__str__())

    def test_user_empty_cv_name_(self):
        self.assertEqual(self.profile.get_file_name(), None)

    def test_calculate_success_rate_less_than_one(self):
        self.assertEqual(self.profile.calculate_success_rate(), 0)

    def test_calculate_success_rate_greater_than_one(self):
        self.profile.total_job_done = 2
        self.profile.total_hired = 3
        self.profile.save()
        proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=70,
            status="accepted",
        )

        self.assertEqual(self.profile.calculate_success_rate(), 100)

    def test_calculate_rating_less_than_one(self):
        self.assertEqual(self.profile.calculate_rating(), 0)

    def test_calculate_rating_greater_than_one(self):
        self.profile.total_job_done = 1
        self.profile.total_hired = 3
        self.profile.save()
        proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=70,
            status="accepted",
        )

        self.assertEqual(self.profile.calculate_rating(), 2.5)

    def test_calculate_on_budget_and_time_less_than_one(self):
        self.assertEqual(self.profile.calculate_onBudget(), 0)
        self.assertEqual(self.profile.calculate_onTime(), 0)

    def test_calculate_on_budget_and_time_greater_than_one(self):
        proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=70,
            status="completed",
            onBudget=True,
            onTime=True,
        )

        self.assertEqual(self.profile.calculate_onBudget(), 100)
        self.assertEqual(self.profile.calculate_onTime(), 100)

    def test_rating(self):
        self.assertEqual(self.profile.get_rating(), 0)
        self.profile.rating = 2.5
        self.assertEqual(self.profile.get_rating(), 2.5)

    def test_bookmark_profile_user_not_authenticated(self):
        bookmark = Bookmark.objects.create(
            user=self.user2,
            freelancer_profile=self.profile,
        )
        self.assertEqual(self.profile.get_bookmark_profile(), False)

    # TODO: find alternative way to test the get_current_user()
    # def test_bookmark_profile_user_is_authenticated(self):
    #     bookmark = Bookmark.objects.create(
    #         user=self.user2,
    #         freelancer_profile=self.profile,
    #     )
    #     self.client.login(email='test2@email.com', password='12345')
    #     user = auth.get_user(self.client)
    #     self.assertEqual(user.is_authenticated, True)
    #     self.assertEqual(self.profile.get_bookmark_profile(), True)
