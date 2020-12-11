from django.http import HttpResponseBadRequest, JsonResponse
from django.test import TestCase
from django.urls import reverse, resolve
from django.db.models import signals

from accounts.models import User, Profile
from employer import views
from employer.forms import TaskForm, experience_level
from employer.models import skills, PostTask, Offers
from freelancers.models import Proposal
from notification.models import Notification


class TestLoginAndEmployerRequired(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345")
        self.patterns = [
            ("post_task", None),
            ("my_tasks", None),
            ("edit_task", {"id": 1}),
            ("delete_task", {"id": 1}),
            ("manage_proposal", {"id": 1}),
            ("accept_proposal", {"id": 1}),
            ("emp_dashboard", None),
            ("emp_reviews", None),
            ("post_reviews", {"id": 1}),
            ("send_offer", None),
        ]

    def test_redirection(self):
        for url_name, kwargs in self.patterns:
            url = reverse(url_name, kwargs=kwargs)
            next_url = f'/?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, next_url)

    def test_not_employer_redirection(self):
        self.client.login(email="khan@email.com", password="khan12345")
        for url_name, kwargs in self.patterns:
            url = reverse(url_name, kwargs=kwargs)
            next_url = f'/?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, next_url)


class TestPostCreateTaskView(TestCase):
    def setUp(self):
        self.url = reverse('post_task')
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345", is_Employer=True)
        self.client.login(email="khan@email.com", password="khan12345")

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/postTask/')
        self.assertEqual(view.func.view_class, views.PostTaskView)

    def test_invalid_data(self):
        data = {
            "title": "",
            "skills": skills[12],
            "tags": "Swift + Objective C",
            "min_price": 20,
            "max_price": 40,
            "exp_level": "expert",
            "project_type": "fixed",
        }
        response = self.client.post(self.url, data)
        form = response.context.get("form")
        self.assertTrue(response.status_code, 200)
        self.assertIsInstance(form, TaskForm)
        self.assertTemplateUsed(response, "Employer/postATask.html")
        self.assertContains(response, "This field is required.")

    def test_valid_data(self):
        data = {
            "title": "IOS project",
            "skills": skills[12],
            "tags": "Swift + Objective C",
            "min_price": 20,
            "max_price": 40,
            "exp_level": experience_level[2][0],
            "project_type": "fixed",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PostTask.objects.count(), 1)
        self.assertEqual(PostTask.objects.last().title, "IOS project")
        self.assertRedirects(response, reverse('my_tasks'))


class TestMyTaskView(TestCase):
    def setUp(self):
        self.url = reverse('my_tasks')
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.client.login(email="test@email.com", password="khan12345")

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/tasks/')
        self.assertEqual(view.func, views.my_tasks)

    def test_response_context(self):
        for i in range(5):
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

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostTask.objects.count(), 5)
        self.assertEqual(PostTask.objects.last().user, self.user)
        self.assertEqual(PostTask.objects.last().title, "IOS project 4")
        self.assertIn("tasks", response.context)
        self.assertEqual(len(response.context.get("tasks")), 4)
        self.assertTemplateUsed(response, "Employer/myTasks.html")


class TestEditTaskView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        # self.client.login(email="test@email.com", password="khan12345")
        self.post = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.url = reverse('edit_task', kwargs={"id": 1})

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/task/1/edit/')
        self.assertEqual(view.func, views.edit_task)

    def test_invalid_user(self):
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        self.client.login(email="test@email.com", password="khan12345")
        url = reverse('edit_task', kwargs={"id": 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_job_in_progress(self):
        self.client.login(email="test@email.com", password="khan12345")
        task = PostTask.objects.create(
            user=self.user,
            title="java project",
            skills=skills[12],
            tags="java + spring-boot",
            min_price=200,
            max_price=400,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="In Progress",
        )
        url = reverse("edit_task", kwargs={"id": task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_response_get_context(self):
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTemplateUsed(response, "Employer/postATask.html")

    def test_response_post_request(self):
        self.client.login(email="test@email.com", password="khan12345")
        data = {
            "title": "java project",
            "skills": skills[12],
            "tags": "Swift + Objective C",
            "min_price": 200,
            "max_price": 400,
            "exp_level": experience_level[2][0],
            "project_type": "fixed",
        }
        response = self.client.post(self.url, data)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.title, "java project")
        self.assertRedirects(response, reverse("my_tasks"))


class TestDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        # self.client.login(email="test@email.com", password="khan12345")
        self.post = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.url = reverse('delete_task', kwargs={"id": 1})
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/task/1/delete/')
        self.assertEqual(view.func, views.delete_task)

    def test_invalid_user(self):
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        self.client.login(email="test@email.com", password="khan12345")
        url = reverse('delete_task', kwargs={"id": 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_without_ajax(self):
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response, HttpResponseBadRequest)

    def test_job_in_progress(self):
        self.client.login(email="test@email.com", password="khan12345")
        post = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="In Progress"
        )
        url = reverse('delete_task', kwargs={"id": post.id})
        response = self.client.post(url, {}, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "Your are not permitted to perform this action")

    def test_job_completed(self):
        self.client.login(email="test@email.com", password="khan12345")
        post = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed"
        )
        url = reverse('delete_task', kwargs={"id": post.id})
        response = self.client.post(url, {}, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "Your are not permitted to perform this action")

    def test_response_context(self):
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.post(self.url, {}, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertContains(response, "delete successfully")
        self.assertEqual(PostTask.objects.count(), 0)
        self.assertIsInstance(response, JsonResponse)


class TestManageProposalView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        user3 = User.objects.create_user(email="test3@email.com", password="khan12345", is_Freelancer=True)
        Profile.objects.create(
            user=user3,
            rate=20,
            skills=['Java', 'Python'],
        )

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
        for i in range(1, 5):
            Proposal.objects.create(
                user=user3,
                task=self.task,
                rate=i * 10,
                days=i,
            )

        self.url = reverse('manage_proposal', kwargs={"id": 1})

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/proposal/1/manage/')
        self.assertEqual(view.func, views.manage_proposal)

    def test_invalid_user(self):
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        self.client.login(email="test@email.com", password="khan12345")
        url = reverse('manage_proposal', kwargs={"id": 2})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_response_context(self):
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Proposal.objects.count(), 4)
        self.assertEqual(Proposal.objects.last().rate, 40)
        self.assertIn("task", response.context)
        self.assertIn("proposals", response.context)
        self.assertEqual(len(response.context.get("proposals")), 3)
        self.assertTemplateUsed(response, "Employer/ManageProposal.html")


class TestAcceptProposalView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user3 = User.objects.create_user(email="test3@email.com", password="khan12345", is_Freelancer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        Profile.objects.create(
            user=self.user3,
            rate=20,
            skills=['Java', 'Python'],
        )
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
        self.proposal = Proposal.objects.create(
            user=self.user3,
            task=self.task,
            rate=40,
            days=3,
        )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse("accept_proposal", kwargs={"id": self.proposal.id})

    def test_without_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalid_id(self):
        url = reverse('accept_proposal', kwargs={"id": 2})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_user(self):
        User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.client.logout()
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.post(self.url, {}, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "You are not permitted to perform this action."})

    def test_accepted_proposal(self):
        user = User.objects.create_user(email="testuser@email.com", password="khan12345", is_Freelancer=True)
        proposal = Proposal.objects.create(
            user=user,
            task=self.task,
            rate=50,
            days=60,
            status="accepted",
        )
        response = self.client.post(reverse('accept_proposal', kwargs={"id": proposal.id}), **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "Sorry your are not assign this job to multiple user."})

    def test_task_completed(self):
        user = User.objects.create_user(email="testuser@email.com", password="khan12345", is_Freelancer=True)
        proposal = Proposal.objects.create(
            user=user,
            task=self.task,
            rate=50,
            days=60,
            status="completed",
        )
        response = self.client.post(reverse('accept_proposal', kwargs={"id": proposal.id}), **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "Your job is completed"})

    def test_success_result(self):
        response = self.client.post(self.url, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['msg'], "Proposal accepted.")
        self.user3.refresh_from_db()
        self.task.refresh_from_db()
        self.proposal.refresh_from_db()
        self.assertEqual(self.user3.profile.total_hired, 1)
        self.assertEqual(self.task.job_status, "In Progress")
        self.assertEqual(self.proposal.status, "accepted")


class TestDashboardView(TestCase):
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
            project_type="fixed",
        )
        for i in range(7):
            Notification.objects.create(
                actor=self.user2,
                recipient=self.user,
                target=self.task,
                action=Notification.PLACE_A_BID,
            )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse("emp_dashboard")

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.context)
        self.assertIn("notifications", response.context)
        self.assertEqual(len(response.context['notifications']), 5)
        self.assertTemplateUsed(response, "Employer/Dashboard.html")

    def test_ajax_request(self):
        response = self.client.get(self.url, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertIn("notifications", response.context)
        self.assertIsInstance(response, JsonResponse)


class TestReviewsView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        task1 = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        task2 = PostTask.objects.create(
            user=self.user,
            title="java project",
            skills=skills[12],
            tags="java",
            min_price=200,
            max_price=400,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        task3 = PostTask.objects.create(
            user=self.user,
            title="C# project",
            skills=skills[12],
            tags="C sharp + .NET",
            min_price=200,
            max_price=400,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        task4 = PostTask.objects.create(
            user=self.user,
            title="Python project",
            skills=skills[12],
            tags="Python + Django",
            min_price=150,
            max_price=300,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        Proposal.objects.create(
            user=self.user2,
            task=task1,
            rate=40,
            days=3,
            status="completed"
        )
        Proposal.objects.create(
            user=self.user2,
            task=task2,
            rate=40,
            days=3,
            status="completed"
        )
        Proposal.objects.create(
            user=self.user2,
            task=task3,
            rate=40,
            days=3,
            status="completed"
        )
        Proposal.objects.create(
            user=self.user2,
            task=task4,
            rate=40,
            days=3,
            status="completed"
        )
        self.url = reverse('emp_reviews')
        self.client.login(email="test@email.com", password="khan12345")

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/reviews/')
        self.assertEqual(view.func, views.reviews)

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("proposals", response.context)
        self.assertEqual(len(response.context['proposals']), 3)
        self.assertTemplateUsed(response, "Employer/Reviews.html")


class TestPostReviewsView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.task = PostTask.objects.create(
            user=self.user,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        self.proposal = Proposal.objects.create(
            user=self.user2,
            task=self.task,
            rate=40,
            days=3,
            status="completed"
        )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse('post_reviews', kwargs={"id": self.proposal.id})

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/reviews/1/')
        self.assertEqual(view.func, views.post_reviews)

    def test_without_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_user(self):
        self.client.logout()
        user = User.objects.create_user(email="tes3@email.com", password="khan12345", is_Employer=True)
        self.client.login(email="tes3@email.com", password="khan12345")
        task = PostTask.objects.create(
            user=user,
            title="Html admin panel",
            skills=skills[12],
            tags="Html + CSS",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
            job_status="Completed",
        )
        proposal = Proposal.objects.create(
            user=self.user2,
            task=task,
            rate=40,
            days=3,
            status="completed"
        )
        response = self.client.post(self.url, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, 'errors': "You are not permitted to perform this action."})

    def test_success_result(self):
        data = {
            "onBudget": "yes",
            "onTime": "yes",
            "rating": 4.00,
            "comment": "great work"
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.proposal.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True, 'msg': "Review submitted"})
        self.assertEqual(self.proposal.onBudget, True)
        self.assertEqual(self.proposal.onTime, True)
        self.assertEqual(self.proposal.rating, 4.00)
        self.assertEqual(self.proposal.comment, "great work")
        self.assertIsInstance(response, JsonResponse)


class TestSendOffersView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Employer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse('send_offer')
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        Profile.objects.create(
            user=self.user2,
            rate=20,
            skills=['Java', 'Python'],
        )

    def test_url_resolves_correct_view(self):
        view = resolve('/employer/offer/')
        self.assertEqual(view.func, views.send_offers)

    def test_without_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_profile(self):
        data = {
            "profile_id": 2,
            "email": "test@email.com",
            "full_name": "umair khan",
            "offer_message": "hi! i need one python script."
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_invalid_data(self):
        data = {
            "profile_id": 1,
            "email": "test@email.com",
            "full_name": "khan"
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertIsInstance(response, JsonResponse)

    def test_success_result(self):
        data = {
            "profile_id": 1,
            "email": "test@email.com",
            "full_name": "umair khan",
            "offer_message": "hi! i need one python script."
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True, "msg": "Offer send"})
        self.assertEqual(Offers.objects.count(), 1)
