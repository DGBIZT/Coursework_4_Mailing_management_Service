from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()


class MessageManagement(models.Model):
    message_subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        help_text = "Краткий заголовок письма, отображается в поле «Тема» у получателя."
    )

    body = models.TextField(
        verbose_name="Тело письма",
        help_text="Содержание письма."
    )

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name='messages'
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["message_subject"]

    def __str__(self):
        return self.message_subject