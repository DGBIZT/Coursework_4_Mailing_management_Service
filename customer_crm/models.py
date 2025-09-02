from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import EmailValidator

class MailingRecipient(models.Model):
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[EmailValidator()],
        verbose_name='E-Mail Address'
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name='Ф.И.О.'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )
    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"
        ordering = ['email']

    def __str__(self):
        return self.full_name

    def clean(self):
        # Дополнительная валидация данных
        if self.full_name:
            # Проверяем, что в Ф.И.О. нет цифр
            if any(char.isdigit() for char in self.full_name):
                raise ValidationError({'full_name': 'Ф.И.О. не должно содержать цифр'})

