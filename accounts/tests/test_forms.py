from django.test import TestCase

from accounts.forms import CustomUserForm


class TestCustomUserForm(TestCase):

    def test_save_method(self):
        form = CustomUserForm(data={
            "email": "test@email.com",
            "password1": "khan1234",
            "password2": "khan1234",
            "account-type": "Freelancer",

        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.is_Freelancer)
        self.assertFalse(user.is_Employer)
