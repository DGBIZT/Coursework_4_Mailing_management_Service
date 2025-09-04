from django.db import models
from django.utils import timezone
from messages_mgmt.models import MessageManagement
from customer_crm.models import MailingRecipient

class Mailing(models.Model):

    #Временные параметры
    start_datetime = models.DateTimeField(
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
        default='Created'
    )

    # Связь с сообщением
    message = models.ForeignKey(
        MessageManagement, # модель, с которой устанавливается связь
        verbose_name='Сообщение',
        on_delete=models.CASCADE,
        related_name='related_mailings',
    )

    # Связь с получателями
    recipients = models.ManyToManyField(
        MailingRecipient, # модель, с которой устанавливается связь
        verbose_name='Получатели',
        related_name='recipient_mailings',
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-start_datetime'] # порядок сортировки объектов по умолчанию, ‘-’ перед полем означает сортировку по убыванию
                                       # В данном случае объекты будут сортироваться по полю start_datetime от новых к старым

    def __str__(self):
        return f"Рассылка #{self.id} ({self.get_status_display()})"