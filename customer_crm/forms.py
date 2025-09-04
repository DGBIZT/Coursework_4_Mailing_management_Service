from django import forms
from django.core.exceptions import ValidationError

from .models import MailingRecipient

# Список запрещённых слов
FORBIDDEN_WORDS = {
    'admin', 'administrator', 'root', 'support', 'help',  "спам", 'casino', 'sex', 'info', 'webmaster',
    'moderator', 'owner', 'fckyou', 'btch', 'bestshop', 'freemoney', 'casino777', 'sexchat', 'aaaaaaaaaa',
    '11111111', 'qwertyuiop',
}
def validate_forbidden_words(value):
    """
    Проверяет, что текст не содержит запрещённых слов.
    """
    words = value.lower().split()
    cleaned_words = {word.strip(".,?!:;\"'()[]{}") for word in words}
    found = FORBIDDEN_WORDS.intersection(cleaned_words)
    if found:
        raise ValidationError(f"Недопустимые слова: {', '.join(found)}")


class MailingRecipientFrom(forms.ModelForm):
    class Meta:
        model = MailingRecipient
        fields = ["email", "full_name", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder' : 'Введите вашу почту'
        })

        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите Ф.И.О.'
        })

        self.fields['comment'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите комментарий'
        })

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        full_name = cleaned_data.get('full_name')

        if email and full_name and email.lower() == full_name.lower():
            self.add_error('email', 'Email и Ф.И.О. не могут быть одинаковыми')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_forbidden_words(email)
        allowed_domains = ('@gmail.com', '@sky.pro', '@yandex.ru', '@mail.com')
        if not email.endswith(allowed_domains):
            raise ValidationError("Email должен оканчиваться на @gmail.com, @yandex.ru, @mail.ru или @sky.pro")
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        validate_forbidden_words(full_name)
        return full_name

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        validate_forbidden_words(comment)
        return comment