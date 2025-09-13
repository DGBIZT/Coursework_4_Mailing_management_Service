from django import forms
from django.core.exceptions import ValidationError
from .models import MessageManagement

class MessageManagementForm(forms.ModelForm):
    class Meta:
        model = MessageManagement
        fields = ['message_subject', 'body']
        widgets = {
            'message_subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите тему письма'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Введите текст сообщения'
            })
        }
        labels = {
            'message_subject': 'Тема письма',
            'body': 'Текст сообщения'
        }
        help_texts = {
            'message_subject': 'Краткий заголовок письма, отображается в поле «Тема» у получателя',
            'body': 'Содержание письма'
        }

    def clean_message_subject(self):
        subject = self.cleaned_data['message_subject']
        if len(subject) < 5:
            raise ValidationError('Тема должна содержать минимум 5 символов')
        return subject

    def clean_body(self):
        body = self.cleaned_data['body']
        if len(body) < 10:
            raise ValidationError('Текст сообщения должен содержать минимум 10 символов')
        return body

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('message_subject')
        body = cleaned_data.get('body')

        if subject and body:
            if subject.lower() in body.lower():
                self.add_error('message_subject', 'Тема не должна повторяться в тексте сообщения')
