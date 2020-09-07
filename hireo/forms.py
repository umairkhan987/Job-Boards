from django import forms

from .models import Offers


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offers
        fields = ('full_name', 'email', 'offer_message', 'offer_file')
