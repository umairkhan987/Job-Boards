from django.db.models import signals
from django.http import JsonResponse
from django.test import TestCase
from django.urls import reverse, resolve

from accounts.models import User, Profile
from employer.forms import experience_level
from employer.models import PostTask, skills, Offers
from freelancers import views
from freelancers.models import Proposal
from notification.models import Notification


class TestLoginAndFreelancerRequired(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345")
        self.patterns = [
            ("submit_proposals", None),
            ("my_proposals", None),
            ("delete_proposal", {"id": 1}),
            ("cancel_task", {"id": 1}),
            ("task_completed", {"id": 1}),
            ("freelancer_dashboard", None),
            ("offers", None),
            ("delete_offer", {"id": 1}),
            ("freelancer_reviews", None),
        ]

    def test_redirection(self):
        for url_name, kwargs in self.patterns:
            url = reverse(url_name, kwargs=kwargs)
            next_url = f'/?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, next_url)

    def test_not_freelancer_redirection(self):
        self.client.login(email="khan@email.com", password="khan12345")
        for url_name, kwargs in self.patterns:
            url = reverse(url_name, kwargs=kwargs)
            next_url = f'/?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, next_url)


class TestSubmitProposalView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.url = reverse('submit_proposals')
        self.task = PostTask.objects.create(
            user=self.user2,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.client.login(email="khan@email.com", password="khan12345")

    def test_without_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_invalid_task(self):
        response = self.client.post(self.url, {"task_id": 2}, **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_multiple_proposal_from_same_user(self):
        Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=30,
            days=2,
        )
        response = self.client.post(self.url, {"task_id": self.task.id}, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "You bid has already been submitted."})

    def test_invalid_data(self):
        data = {
            "task_id": 1,
            "days": 2,
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "This field is required.")

    def test_success_result(self):
        data = {
            "task_id": 1,
            "rate": 30,
            "days": 2,
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertContains(response, "Your bid has been submitted.")
        self.assertIsInstance(response, JsonResponse)


class TestMyProposalView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.url = reverse('my_proposals')
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.client.login(email="test@email.com", password="khan12345")
        self.task = PostTask.objects.create(
            user=self.user2,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        for i in range(5):
            Proposal.objects.create(
                user=self.user,
                task=self.task,
                rate=30,
                days=2,
            )

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancer/myProposals/')
        self.assertEqual(view.func, views.my_proposals)

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Proposal.objects.count(), 5)
        self.assertEqual(Proposal.objects.last().user, self.user)
        self.assertIn("proposals", response.context)
        self.assertEqual(len(response.context.get("proposals")), 4)
        self.assertTemplateUsed(response, "Freelancer/MyProposals.html")


class TestDeleteProposalView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.client.login(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.task = PostTask.objects.create(
            user=self.user2,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=30,
            days=2,
        )
        self.url = reverse('delete_proposal', kwargs={"id": self.proposal.id})

    def test_invalid_user(self):
        self.client.logout()
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        url = reverse('delete_proposal', kwargs={"id": 2})
        response = self.client.post(url, **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_proposal_status_accepted(self):
        proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=30,
            days=2,
            status="accepted"
        )
        response = self.client.post(reverse('delete_proposal', kwargs={"id": proposal.id}), **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "You are not permitted to delete this Proposal"})

    def test_success_result(self):
        response = self.client.post(self.url, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['deleted'], True)
        self.assertEqual(Proposal.objects.count(), 0)
        self.assertContains(response, "Proposal successfully deleted.")
        self.assertContains(response, "Currently you have not placed any bid yet.")


class TestCancelTaskView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.client.login(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
        )
        self.task = PostTask.objects.create(
            user=self.user2,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=30,
            days=2,
        )
        self.url = reverse('cancel_task', kwargs={"id": self.proposal.id})

    def test_invalid_user(self):
        self.client.logout()
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        url = reverse('cancel_task', kwargs={"id": 2})
        response = self.client.post(url, **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_success_result(self):
        response = self.client.post(self.url, **self.kwargs)
        self.proposal.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": True, "msg": "Job cancelled."})
        self.assertEqual(self.proposal.status, "cancelled")
        self.assertEqual(self.proposal.task.job_status, "Pending")
        self.assertIsInstance(response, JsonResponse)


class TestTaskCompletedView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.client.login(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
            total_hired=1
        )
        self.task = PostTask.objects.create(
            user=self.user2,
            title="IOS project",
            skills=skills[12],
            tags="Swift + Objective C",
            min_price=20,
            max_price=40,
            exp_level=experience_level[2][0],
            project_type="fixed",
        )
        self.proposal = Proposal.objects.create(
            user=self.user,
            task=self.task,
            rate=30,
            days=2,
        )
        self.url = reverse('task_completed', kwargs={"id": self.proposal.id})

    def test_invalid_user(self):
        self.client.logout()
        self.client.login(email="test2@email.com", password="khan12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_invalid_id(self):
        url = reverse('task_completed', kwargs={"id": 2})
        response = self.client.post(url, **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_success_result(self):
        response = self.client.post(self.url, **self.kwargs)
        self.proposal.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": True, "msg": "Job Completed."})
        self.assertEqual(self.proposal.status, "completed")
        self.assertEqual(self.proposal.task.job_status, "Completed")
        self.assertEqual(self.user.profile.total_job_done, 1)
        self.assertIsInstance(response, JsonResponse)


class TestDashboardView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
        )
        self.offer = Offers.objects.create(
            profile=self.profile,
            sender=self.user2,
            full_name="khan",
            email="test2@email.com",
            offer_message="Hi i need react admin panel."
        )
        for i in range(7):
            Notification.objects.create(
                actor=self.user2,
                recipient=self.user,
                target=self.offer,
                action=Notification.MAKE_OFFER,
            )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse('freelancer_dashboard')

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancer/dashboard/')
        self.assertEqual(view.func, views.dashboard)

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("labels", response.context)
        self.assertIn("data", response.context)
        self.assertIn("notifications", response.context)
        self.assertEqual(len(response.context['notifications']), 5)
        self.assertTemplateUsed(response, "Freelancer/Dashboard.html")

    def test_ajax_request(self):
        response = self.client.get(self.url, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertIn("notifications", response.context)
        self.assertIsInstance(response, JsonResponse)


class TestOffersView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
        )
        for i in range(5):
            Offers.objects.create(
                profile=self.profile,
                sender=self.user2,
                full_name="khan",
                email="test2@email.com",
                offer_message=f"Hi i need {i} react admin panel."
            )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse('offers')

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancer/offers/')
        self.assertEqual(view.func, views.offers)

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("offers", response.context)
        self.assertEqual(len(response.context['offers']), 4)
        self.assertTemplateUsed(response, "Freelancer/Offers.html")


class TestDeleteOfferView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.profile = Profile.objects.create(
            user=self.user,
            rate=20,
            skills=['Java', 'Python'],
        )
        self.offer = Offers.objects.create(
            profile=self.profile,
            sender=self.user2,
            full_name="khan",
            email="test2@email.com",
            offer_message="Hi i need react admin panel."
        )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse("delete_offer", kwargs={"id": self.offer.id})

    def test_invalid_id(self):
        response = self.client.post(reverse("delete_offer", kwargs={"id": 3}), **self.kwargs)
        self.assertEqual(response.status_code, 404)

    def test_invalid_user(self):
        user = User.objects.create_user(email="test3@email.com", password="khan12345", is_Freelancer=True)
        profile = Profile.objects.create(
            user=user,
            rate=20,
            skills=['Java', 'Python'],
        )
        offer = Offers.objects.create(
            profile=profile,
            sender=self.user2,
            full_name="khan",
            email="test2@email.com",
            offer_message="Hi i need react admin panel."
        )
        response = self.client.post(reverse("delete_offer", kwargs={"id": offer.id}), **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"),
                             {"success": False, "errors": "You are not permitted to perform this operation."})

    def test_success_result(self):
        response = self.client.post(self.url, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertContains(response, "There is no offers.")
        self.assertEqual(Offers.objects.count(), 0)


class TestReviewView(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = User.objects.create_user(email="test@email.com", password="khan12345", is_Freelancer=True)
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Employer=True)
        self.task = PostTask.objects.create(
            user=self.user2,
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
                user=self.user,
                task=self.task,
                rate=30,
                days=2,
                status="completed",
                rating=i
            )
        self.client.login(email="test@email.com", password="khan12345")
        self.url = reverse('freelancer_reviews')

    def test_url_resolves_correct_view(self):
        view = resolve('/freelancer/reviews/')
        self.assertEqual(view.func, views.reviews)

    def test_success_result(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("proposals", response.context)
        self.assertEqual(len(response.context['proposals']), 3)
        self.assertTemplateUsed(response, "Freelancer/Reviews.html")
