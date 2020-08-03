from django.contrib.auth.forms import UserCreationForm
from django import forms

from accounts.models import User, Profile


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'is_Employer', 'is_Freelancer')

    def save(self, commit=True):
        user = super().save(commit=False)
        account_type = self.data.get('account-type')
        if account_type == "Freelancer":
            user.is_Freelancer = True
        else:
            user.is_Employer = True
        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profileImg')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('rate', 'skills', 'tags', 'country', 'introduction', 'userCV')
