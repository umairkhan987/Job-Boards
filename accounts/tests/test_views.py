from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.test import TestCase
from django.urls import reverse, resolve

from accounts import views
from accounts.forms import ProfileForm, UserForm, country_names
from accounts.models import User, Profile, skills


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="12345")
        self.login_url = reverse("login")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_login_view(self):
        credentials = {
            "username": "test@email.com",
            "password": "12345",
        }
        response = self.client.post(self.login_url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding="utf8"), {"success": True, 'msg': "Successfully Login"})
        # wrong credentials
        credentials = {
            "username": "test@email.com",
            "password": "1234567",
        }
        response = self.client.post(self.login_url, credentials, **self.kwargs)
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
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def test_without_ajax_request(self):
        credentials = {
            "email": "test@email.com",
            "password": "12345",
            "account-type": "Employer",
        }
        response = self.client.post(self.register_url, credentials)
        self.assertEqual(response.status_code, 400)
        response = self.client.get(self.register_url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 400)

    def test_user_register(self):
        credentials = {
            "email": "test@email.com",
            "password1": "khan1234",
            "password2": "khan1234",
            "account-type": "Freelancer",
        }
        response = self.client.post(self.register_url, credentials, **self.kwargs)
        user = User.objects.get(email="test@email.com")
        self.assertNotEqual(user.profile, None)
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
        response = self.client.post(self.register_url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 400)

        # incorrect password less then 8 character
        credentials = {
            "email": "test.com",
            "password1": "khan123",
            "password2": "khan123",
            "account-type": "Freelancer",
        }
        response = self.client.post(self.register_url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 400)


class TestLoginRequired(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345", is_Freelancer=True)
        self.patterns = [
            ("settings", None),
            ("change-password", None),
            ("update-account", None),
            ("update-profile", None),
        ]

    def test_redirection(self):
        for url_name, kwargs in self.patterns:
            url = reverse(url_name, kwargs=kwargs)
            next_url = f'/?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, next_url)


class TestSettingView(TestCase):
    def setUp(self):
        self.url = reverse('settings')
        self.user = User.objects.create_user(email="khan@email.com", password="khan12345", is_Freelancer=True)
        self.client.login(email="khan@email.com", password="khan12345")

    def test_url_resolves_correct_view(self):
        view = resolve('/account/settings/')
        self.assertEqual(view.func.view_class, views.SettingView)

    def test_form(self):
        response = self.client.get(self.url)
        form = response.context.get('form')
        psd_form = response.context.get('password_form')
        profile_form = response.context.get('profile_form')
        self.assertIsInstance(psd_form, PasswordChangeForm)
        self.assertIsInstance(form, UserForm)
        # if user is freelancer
        self.assertIsInstance(profile_form, ProfileForm)

    def test_setting_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Hireo/settings.html")


class TestChangePasswordView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.url = reverse('change-password')
        self.client.login(email="test@email.com", password="khan12345")

    def test_without_ajax_request(self):
        credentials = {
            "old_password": "khan12345",
            "new_password1": "khan9876",
            "new_password2": "khan9876",
        }
        response = self.client.post(self.url, credentials)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response, HttpResponseBadRequest)

    def test_valid_password(self):
        credentials = {
            "old_password": "khan12345",
            "new_password1": "khan9876",
            "new_password2": "khan9876",
        }
        response = self.client.post(self.url, credentials, **self.kwargs)
        self.user.refresh_from_db()
        form = response.context.get('password_form')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(self.user.check_password("khan9876"), True)
        self.assertIsInstance(form, PasswordChangeForm)
        self.assertIsInstance(response, JsonResponse)

    def test_invalid_password(self):
        credentials = {
            "old_password": "khan123",
            "new_password1": "khan9876",
            "new_password2": "khan9876",
        }
        response = self.client.post(self.url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "Your old password was entered incorrectly.")


class TestUpdateAccountView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@email.com", password="khan12345")
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.url = reverse('update-account')
        self.client.login(email="test@email.com", password="khan12345")

    def test_without_ajax_request(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response, HttpResponseBadRequest)

    def test_valid_data(self):
        credentials = {
            "first_name": "test",
            "last_name": "abc"
        }
        response = self.client.post(self.url, credentials, **self.kwargs)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(self.user.first_name, "test")
        self.assertEqual(self.user.last_name, "abc")
        self.assertIn("form", response.context)
        form = response.context.get('form')
        self.assertIsInstance(form, UserForm)
        self.assertIsInstance(response, JsonResponse)

    def test_invalid_data(self):
        credentials = {
            "first_name": "",
            "last_name": "abc"
        }
        response = self.client.post(self.url, credentials, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertContains(response, "This field is required")
        self.assertIsInstance(response, JsonResponse)


class TestUpdateProfileView(TestCase):
    def setUp(self):
        self.user2 = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.url = reverse('update-profile')
        self.client.login(email="test2@email.com", password="khan12345")

    def test_not_freelancer_redirection(self):
        self.client.logout()
        user = User.objects.create_user(email="test@email.com", password="khan12345")
        self.client.login(email="test@email.com", password="khan12345")
        next_url = f'/?next={self.url}'
        response = self.client.get(self.url)
        self.assertRedirects(response, next_url)

    def test_without_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response, HttpResponseBadRequest)

    def test_invalid_data(self):
        data = {
            "rate": 2,
            "country": country_names[12],
            "skills": skills[13],
            "tags": "",
            "introduction": "i need"
        }
        response = self.client.post(self.url, data, **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertIn("profile_form", response.context)
        self.assertIsInstance(response, JsonResponse)
        # rate is greater then 5
        self.assertContains(response, 'Ensure this value is greater than or equal to 5.')
        # tag required
        self.assertContains(response, "This field is required")
        # introduction min character length 10
        self.assertContains(response, 'Ensure this value has at least 10 characters (it has 6).')


class TestUpdateProfileViewSuccessTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test2@email.com", password="khan12345", is_Freelancer=True)
        self.kwargs = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        self.url = reverse('update-profile')
        self.client.login(email="test2@email.com", password="khan12345")
        data = {
            "rate": 20,
            "country": country_names[12],
            "skills": skills[13],
            "tags": "IOS + Devops",
            "introduction": "i need an ios developer"
        }
        self.response = self.client.post(self.url, data, **self.kwargs)

    def test_status_code_200(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.json()['success'], True)

    def test_is_instance(self):
        self.assertIn("profile_form", self.response.context)
        self.assertIsInstance(self.response, JsonResponse)

    def test_success(self):
        self.user.refresh_from_db()
        self.assertEqual(20, self.user.profile.rate)
        self.assertEqual(country_names[12][1], self.user.profile.country)
        self.assertEqual(skills[13], tuple(self.user.profile.skills))
        self.assertEqual("IOS + Devops", self.user.profile.tags)
        self.assertEqual("i need an ios developer", self.user.profile.introduction)
