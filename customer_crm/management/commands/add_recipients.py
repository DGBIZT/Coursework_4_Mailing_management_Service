from django.core.management.base import BaseCommand
from customer_crm.models import MailingRecipient

class Command(BaseCommand):
    help = ("Добавление получателей рассылки через командную строку. Пример: python manage.py add_recipients")

    def handle(self, *args, **kwargs):
        recipient_data = [
            {"email": "anna@sky.pro", "full_name":"Анна Ивановна", "comment":"Получатель Анна"},
            {"email": "boris@sky.pro", "full_name": "Борис Петров", "comment": "Получатель Борис"},
            {"email": "sveta@sky.pro", "full_name": "Света Новикова", "comment": "Получатель Света"},
            {"email": "ekaterina@sky.pro", "full_name": "Екатерина Сидорова", "comment": "Получатель Екатерина"},
        ]

        created_count = 0
        skipped_count = 0

        for data in recipient_data:
            recipient, created = MailingRecipient.objects.get_or_create(
                email=data["email"], # Уникальный ключ — email
                defaults={ # Эти поля будут использованы ТОЛЬКО при создании
                    "full_name": data["full_name"],
                    "comment": data["comment"]
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Добавлен: {recipient.email} {recipient.full_name}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Уже существует: {recipient.email}")
                )
                skipped_count += 1

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Готово: добавлено {created_count}, пропущено {skipped_count}"
            )
        )