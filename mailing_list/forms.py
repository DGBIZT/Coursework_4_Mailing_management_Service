from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Mailing, MailingRecipient
from messages_mgmt.models import MessageManagement


class CompleteMailingForm(forms.ModelForm):
    message = forms.ModelChoiceField(
        queryset=MessageManagement.objects.none(),
        empty_label="Выберите сообщение",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='id',
    )

    class Meta:
        model = Mailing
        fields = ['recipients', 'message']
        widgets = {
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Фильтруем только получателей текущего пользователя
        self.fields['recipients'].queryset = MailingRecipient.objects.filter(user=user)
        # Фильтрация сообщений
        self.fields['message'].queryset = MessageManagement.objects.filter(user=user)

        # Добавляем отладочную информацию
        if not self.fields['message'].queryset.exists():
            print("Сообщения не найдены для пользователя:", user)
            print("Все сообщения:", MessageManagement.objects.all())

    def clean_recipients(self):
        recipients = self.cleaned_data.get('recipients')
        if not recipients:
            raise ValidationError(_('Необходимо выбрать получателей рассылки'))
        return recipients

    def clean_message(self):
        message_obj = self.cleaned_data.get('message')
        if not message_obj:
            raise ValidationError(_('Сообщение не может быть пустым'))

        # Проверяем тело сообщения
        if not message_obj.body.strip():
            raise ValidationError(_('Тело сообщения не может быть пустым'))

        return message_obj

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        recipients = cleaned_data.get('recipients')

        if status == Mailing.STARTED and not recipients:
            self.add_error('status', _('Нельзя запустить рассылку без получателей'))
