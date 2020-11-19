from django.contrib.auth.forms import UserCreationForm
from django import forms

from accounts.models import User, Profile


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'is_Employer', 'is_Freelancer')

    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        account_type = self.data.get('account-type')
        if account_type == "Freelancer":
            user.is_Freelancer = True
        else:
            user.is_Employer = True
        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profileImg')


country_names = [
    ("Australia", "Australia"),
    ("Belgium", "Belgium"),
    ("Brazil", "Brazil"),
    ("Canada", "Canada"),
    ("Colombia", "Colombia"),
    ("Cyprus", "Cyprus"),
    ("Denmark", "Denmark"),
    ("Egypt", "Egypt"),
    ("Hong Kong", "Hong Kong"),
    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Norway", "Norway"),
    ("Pakistan", "Pakistan"),
    ("Panama", "Panama"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Qatar", "Qatar"),
    ("Russia", "Russia"),
    ("Turkey", "Turkey"),
    ("UK", "UK"),
    ("USA", "USA"),
]


class ProfileForm(forms.ModelForm):
    rate = forms.IntegerField(required=True, min_value=5, max_value=200)
    country = forms.ChoiceField(choices=country_names, required=True)
    tags = forms.CharField(required=True, max_length=255)
    introduction = forms.CharField(required=True, widget=forms.Textarea, max_length=2000, min_length=10)

    class Meta:
        model = Profile
        fields = ('rate', 'skills', 'tags', 'country', 'introduction', 'userCV')

    def getCVName(self):
        return self.instance.get_file_name() if self.instance.get_file_name() else None

    # def save(self, commit=True):
    #     profile = super(ProfileForm, self).save(commit=False)
    #     print(self.instance.userCV)
    #     print(self.files)
    #     return profile
