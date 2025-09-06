from django import forms
from .models import Mailing


class CompleteMailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['status']