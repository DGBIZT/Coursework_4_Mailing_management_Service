from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from users.models import CustomUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


class MessageManagement(models.Model):
    message_subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        help_text="Краткий заголовок письма, отображается в поле «Тема» у получателя."
    )

    body = models.TextField(
        verbose_name="Тело письма",
        help_text="Содержание письма."
    )

    user = models.ForeignKey(
        CustomUser,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name='messages'
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["message_subject"]

    def save(self, *args, **kwargs):
        response = super().save(*args, **kwargs)
        # Очищаем кеш при сохранении
        cache.delete(f'messagemanagement_queryset_{self.user.id}')
        return response

    def delete(self, *args, **kwargs):
        # Очищаем кеш перед удалением
        cache.delete(f'messagemanagement_queryset_{self.user.id}')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.message_subject


@receiver(post_save, sender=MessageManagement)
def clear_cache_on_save(sender, instance, **kwargs):
    cache.delete(f'messagemanagement_queryset_{instance.user.id}')


@receiver(post_delete, sender=MessageManagement)
def clear_cache_on_delete(sender, instance, **kwargs):
    cache.delete(f'messagemanagement_queryset_{instance.user.id}')