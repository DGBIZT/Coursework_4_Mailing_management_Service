from django.db import models
from django.db.models import TextField
from django.utils import timezone
from messages_mgmt.models import MessageManagement
from customer_crm.models import MailingRecipient
from datetime import timedelta
from users.models import CustomUser


class Mailing(models.Model):

    start_datetime = models.DateTimeField(  # Временные параметры
        verbose_name="Дата и время первой отправки",
        default=timezone.now
    )
    end_datetime = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        default=timezone.now
    )

    # Статус рассылки
    CREATED = 'Created'
    STARTED = 'Started'
    COMPLETED = 'Completed'

    STATUS_CHOICES = (
        (CREATED, 'Создана'),
        (STARTED, 'Запущена'),
        (COMPLETED, 'Завершена')
    )

    status = models.CharField(
        verbose_name="Статус",
        max_length=10,
        choices=STATUS_CHOICES,
        default=CREATED
    )

    # Связь с сообщением
    message = models.ForeignKey(
        MessageManagement,  # модель, с которой устанавливается связь
        verbose_name='Сообщение',
        on_delete=models.CASCADE,
        related_name='related_mailings',
    )

    # Связь с получателями
    recipients = models.ManyToManyField(
        MailingRecipient,   # модель, с которой устанавливается связь
        verbose_name='Получатели',
        related_name='recipient_mailings',
    )

    user = models.ForeignKey(
        CustomUser,  # или get_user_model()
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='created_mailings'
    )

    is_active = models.BooleanField(
        verbose_name="Активна",
        default=True
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-start_datetime']  # порядок сортировки объектов по умолчанию,
        # ‘-’ перед полем означает сортировку по убыванию
        # В данном случае объекты будут сортироваться по полю
        # start_datetime от новых к старым
        permissions = [
            ('disable_mailing', 'Can disable mailing'),
        ]


class AttemptMailing(models.Model):
    # Временные параметры
    time_attempt = models.DateTimeField(
        verbose_name="Дата и время попытки",
        default=timezone.now
    )

    # Статус
    SUCCESS = 'success'
    FAILURE = 'failure'

    STATUS_CHOICES = (
        (SUCCESS, 'Успешно'),
        (FAILURE, 'Не успешно'),
    )

    status = models.CharField(  # Добавленное поле статуса
        verbose_name="Статус отправки",
        max_length=20,
        choices=STATUS_CHOICES,
        default=SUCCESS
    )

    mail_server_response = models.TextField(
        verbose_name="Ответ почтового сервера",
        blank=True,
        null=True
    )

    mailing = models.ForeignKey(
        Mailing,
        verbose_name="Рассылка",
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='mailings'
    )

    def get_success_rate(self):
        """Процент успешных попыток"""
        total = AttemptMailing.objects.filter(mailing=self.mailing).count()
        success = AttemptMailing.objects.filter(
            mailing=self.mailing,
            status=self.SUCCESS
        ).count()
        return (success / total * 100) if total > 0 else 0

    @classmethod
    def get_user_stats(cls, user):
        # Получаем все сообщения пользователя
        user_messages = MessageManagement.objects.filter(user=user)

        # Получаем все рассылки через связанные сообщения
        mailings = Mailing.objects.filter(message__in=user_messages)

        attempts = cls.objects.filter(mailing__in=mailings)

        return {
            'total_attempts': attempts.count(),
            'success_attempts': attempts.filter(status=cls.SUCCESS).count(),
            'failed_attempts': attempts.filter(status=cls.FAILURE).count(),
        }

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ['-time_attempt']
        permissions = [
            ('view_mailing_stats', 'view mailing stats'), # просмотр статистики
            ('disable_mailing', 'Can disable mailing'),  # существующее право
            ('view_mailing', 'Can view mailing'),  # просмотр рассылок
            ('view_mailingrecipient', 'Can view mailing recipients'),  # просмотр клиентов
            ('view_customuser', 'Can view users'),  # просмотр списка пользователей
            ('block_user', 'Can block users'),  # блокировка пользователей

        ]

    def __str__(self):
        return f"Попытка {self.get_status_display()} от {self.time_attempt}"