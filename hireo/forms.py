from django import forms

from .models import Messages


class MessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ('message_content',)

    def clean_message_content(self):
        content = self.cleaned_data.get('message_content')
        if len(content) > 500:
            raise forms.ValidationError("The message is too long.")
        return content
