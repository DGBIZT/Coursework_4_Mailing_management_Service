from django.core.management.base import BaseCommand
from customer_crm.models import MailingRecipient, CustomUser


class Command(BaseCommand):
    help = ("Добавление получателей рассылки через командную строку. Пример: python manage.py add_recipients. ВНИМАНИЕ с начала создайте пользователя python manage.py createadmin")

    def handle(self, *args, **kwargs):

        # Получаем существующего пользователя
        try:
            admin_user = CustomUser.objects.get(username='testadmin@sky.pro')
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("Пользователь testadmin@sky.pro не найден!"))
            return

        recipient_data = [
            {"email": "anna@sky.pro", "full_name":"Анна Ивановна", "comment":"Получатель Анна", "user": admin_user},
            {"email": "boris@sky.pro", "full_name": "Борис Петров", "comment": "Получатель Борис", "user": admin_user},
            {"email": "sveta@sky.pro", "full_name": "Света Новикова", "comment": "Получатель Света", "user": admin_user},
            {"email": "ekaterina@sky.pro", "full_name": "Екатерина Сидорова", "comment": "Получатель Екатерина", "user": admin_user},
            {"email":"georgiy.gorlov@gmail.com", "full_name":"Горлов Георгий Александрович", "comment": "Реальный получатель", "user": admin_user}
        ]

        created_count = 0
        skipped_count = 0

        for data in recipient_data:
            recipient, created = MailingRecipient.objects.get_or_create(
                email=data["email"],  # Уникальный ключ — email
                defaults={  # Эти поля будут использованы ТОЛЬКО при создании
                    "full_name": data["full_name"],
                    "comment": data["comment"],
                    "user": data["user"]
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