from django import forms

from .models import Proposal


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ('rate', 'days')

    def clean_days(self):
        days = self.cleaned_data.get("days", None)
        if days is not None:
            if int(days) < 1:
                raise forms.ValidationError("Days is greater then 1")
        return days