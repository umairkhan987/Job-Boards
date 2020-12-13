from django.db.models import signals
from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import User, Profile
from employer.forms import experience_level
from employer.models import PostTask, skills
from freelancers.models import Proposal
from hireo import views


class TestIndexView(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('index'))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "Hireo/index.html")

    def test_url_resolves_correct_view(self):
        view = resolve('/')
        self.assertEqual(view.func, views.index)

    def test_response_context(self):
        self.assertIn('total_tasks_posted', self.response.context)
        self.assertIn('total_freelancers', self.response.context)
        self.assertIn('tasks', self.response.context)
        self.assertIn('freelancers', self.response.context)


class TestFindTaskView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        for i in range(1, 7):
            PostTask.objects.create(
                user=self.user,
                title=f"IOS project {i}",
                skills=skills[12],
                tags="Swift + Objective C",
                min_price=20,
                max_price=40,
                exp_level=experience_level[2][0],
                project_type="fixed",
            )
        self.response = self.client.get(reverse('find_tasks'))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "Freelancer/FindTasks.html")

    def test_url_resolves_correct_view(self):
        view = resolve('/tasks/')
        self.assertEqual(view.func, views.findTasks)

    def test_response_context(self):
        self.assertIn('tasks', self.response.context)
        self.assertEqual(len(self.response.context['tasks']), 5)


class TestSingleTaskView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.profile = Profile.objects.create(user=self.user2, rate=20, skills=['Java', 'Python'])
        self.task = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        for i in range(1, 6):
            Proposal.objects.create(
                user=self.user2,
                task=self.task,
                rate=30,
                days=i,
            )

        self.url = reverse('view_task', kwargs={"id": self.task.id})
        self.response = self.client.get(self.url)

    def test_invalid_id(self):
        response = self.client.get(reverse('view_task', kwargs={"id": 2}))
        self.assertEqual(response.status_code, 404)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "Freelancer/ViewTask.html")

    def test_url_resolves_correct_view(self):
        view = resolve('/task/1/')
        self.assertEqual(view.func, views.view_task)

    def test_response_context(self):
        self.assertIn('task', self.response.context)
        self.assertIn('proposals', self.response.context)
        self.assertEqual(len(self.response.context['proposals']), 4)

    def test_ajax_response(self):
        response = self.client.get(self.url, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)


class TestFindFreelancersView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user1 = User.objects.create_user(email="test1@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.user3 = User.objects.create_user(email="test3@email.com", password="khan12345", is_Freelancer=True)
        self.user4 = User.objects.create_user(email="test4@email.com", password="khan12345", is_Freelancer=True)
        self.user5 = User.objects.create_user(email="test5@email.com", password="khan12345", is_Freelancer=True)
        self.user6 = User.objects.create_user(email="test6@email.com", password="khan12345", is_Freelancer=True)
        Profile.objects.create(user=self.user1, rate=20, skills=['Java', 'Python'])
        Profile.objects.create(user=self.user2, rate=20, skills=['Java', 'Python'])
        Profile.objects.create(user=self.user3, rate=20, skills=['Java', 'Python'])
        Profile.objects.create(user=self.user4, rate=20, skills=['Java', 'Python'])
        Profile.objects.create(user=self.user5, rate=20, skills=['Java', 'Python'])
        Profile.objects.create(user=self.user6, rate=20, skills=['Java', 'Python'])
        self.response = self.client.get(reverse('find_freelancer'))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "Employer/FindFreelancer.html")

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancers/')
        self.assertEqual(view.func, views.find_freelancer)

    def test_response_context(self):
        self.assertIn('freelancers', self.response.context)
        # self.assertEqual(len(self.response.context['freelancers']), 5)


class TestSingleFreelancerView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.profile = Profile.objects.create(user=self.user2, rate=20, skills=['Java', 'Python'])
        self.task = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        for i in range(1, 6):
            Proposal.objects.create(
                user=self.user2,
                task=self.task,
                rate=30,
                days=i,
            )

        self.url = reverse('freelancer_profile', kwargs={"id": self.profile.id})
        self.response = self.client.get(self.url)

    def test_invalid_id(self):
        response = self.client.get(reverse('freelancer_profile', kwargs={"id": 2}))
        self.assertEqual(response.status_code, 404)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "Employer/freelancerProfile.html")

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancers/profile/1/')
        self.assertEqual(view.func, views.freelancer_profile)

    def test_response_context(self):
        self.assertIn('work_history', self.response.context)
        self.assertIn('profile', self.response.context)

    def test_ajax_response(self):
        response = self.client.get(self.url, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
