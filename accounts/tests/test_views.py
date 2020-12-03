from django.contrib.auth.forms import PasswordChangeForm
from django.test import TestCase
from django.urls import reverse

from accounts.forms import ProfileForm
from accounts.models import User, Profile


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="12345")
        self.login_url = reverse("login")

    def test_login_view(self):
        credentials = {
            "username": "test@email.com",
            "password": "12345",
        }
        response = self.client.post(self.login_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True, 'msg': "Successfully Login"})
        # wrong credentials
        credentials = {
            "username": "test@email.com",
            "password": "1234567",
        }
        response = self.client.post(self.login_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 404)
        # without ajax
        response = self.client.post(self.login_url, credentials)
        self.assertEqual(response.status_code, 400)
        # get request
        response = self.client.get(self.login_url, credentials)
        self.assertEqual(response.status_code, 400)


class TestRegisterView(TestCase):
    def setUp(self):
        self.register_url = reverse("register")

    def test_without_ajax_request(self):
        credentials = {
            "email": "test@email.com",
            "password": "12345",
            "account-type": "Employer",
        }
        response = self.client.post(self.register_url, credentials)
        self.assertEqual(response.status_code, 400)
        response = self.client.get(self.register_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 400)

    def test_user_register(self):
        credentials = {
            "email": "test@email.com",
            "password1": "khan1234",
            "password2": "khan1234",
            "account-type": "Freelancer",
        }
        response = self.client.post(self.register_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        user = User.objects.get(email="test@email.com")
        self.assertTrue(user.profile)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), {'success': True, 'msg': "Successfully Register"})

    def test_invalid_form_registration(self):
        # incorrect email
        credentials = {
            "email": "test.com",
            "password1": "khan1234",
            "password2": "khan1234",
            "account-type": "Freelancer",
        }
        response = self.client.post(self.register_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 400)

        # incorrect password less then 8 character
        credentials = {
            "email": "test.com",
            "password1": "khan123",
            "password2": "khan123",
            "account-type": "Freelancer",
        }
        response = self.client.post(self.register_url, credentials, **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"})
        self.assertEqual(response.status_code, 400)


class TestSettingView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345", is_Freelancer=True)

    def test_setting_view(self):
        self.client.login(email="khan@email.com", password="khan12345")
        response = self.client.get(reverse('settings'))
        password_form = PasswordChangeForm(user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Hireo/settings.html")
        self.assertEqual(response.context['password_form'].user, password_form.user)
        # if user is freelancer
        profile_form = ProfileForm(instance=self.user.profile)
        self.assertEqual(response.context['profile_form'].instance.user, profile_form.instance.user)


class TestChangePasswordView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_valid_password(self):
        credentials = {
            "old_password": "khan12345",
            "new_password1": "khan9876",
            "new_password2": "khan9876",
        }
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.post(reverse('change-password'), credentials, **self.kwargs)
        # self.assertContains()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)

    def test_invalid_password(self):
        credentials = {
            "old_password": "khan123",
            "new_password1": "khan9876",
            "new_password2": "khan9876",
        }
        self.client.login(email="test@email.com", password="khan12345")
        response = self.client.post(reverse('change-password'), credentials, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "Your old password was entered incorrectly.")