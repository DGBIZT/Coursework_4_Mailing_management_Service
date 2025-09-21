from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from customer_crm.models import MailingRecipient

class Command(BaseCommand):
    help = "Отправляет рассылку выбранным получателям"

    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            help='Тема письма'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Текст сообщения'
        )
        parser.add_argument(
            '--recipients',
            type=str,
            help='Список ID получателей через запятую'
        )

    def handle(self, *args, **kwargs):
        subject = kwargs['subject']
        message = kwargs['message']
        recipients_ids = kwargs['recipients'].split(',') if kwargs['recipients'] else None

        if not subject or not message or not recipients_ids:
            self.stderr.write(self.style.ERROR("Не указаны обязательные параметры"))
            return

        try:
            # Получаем валидных получателей из базы
            valid_recipients = MailingRecipient.objects.filter(
                id__in=recipients_ids
            ).values_list('email', flat=True)

            # Отправляем рассылку
            for email in valid_recipients:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )
                self.stdout.write(self.style.SUCCESS(f"Письмо успешно отправлено на {email}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при отправке: {e}"))

    def is_valid_email(self, email):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
