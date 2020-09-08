from django import forms
from .models import PostTask, Offers

experience_level = (
    ('entry', 'Entry'),
    ('intermediate', 'Intermediate'),
    ('expert', 'Expert')
)


project_choose = [
    ("fixed", 'Fixed Price Project'), ('hourly', 'Hourly Project')
]


class TaskForm(forms.ModelForm):
    exp_level = forms.ChoiceField(choices=experience_level, required=True, )
    project_type = forms.CharField(widget=forms.RadioSelect(choices=project_choose), initial="fixed")
    # skills = forms.MultipleChoiceField(choices=skills, required=True)

    class Meta:
        model = PostTask
        fields = "__all__"
        exclude = ('user', 'created_at', 'updated_at', 'job_status')

    def getFileName(self):
        filename = self.instance.filename()
        if filename:
            return filename
        return None


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offers
        fields = ('full_name', 'email', 'offer_message', 'offer_file')
