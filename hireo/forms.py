from django import forms

from .models import Messages, Offers


class MessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ('message_content',)

    def clean_message_content(self):
        content = self.cleaned_data.get('message_content')
        if len(content) > 500:
            raise forms.ValidationError("The message is too long.")
        return content


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offers
        fields = ('full_name', 'email', 'offer_message', 'offer_file')
