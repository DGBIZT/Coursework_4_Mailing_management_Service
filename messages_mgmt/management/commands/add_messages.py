from django.core.management.base import BaseCommand
from messages_mgmt.models import MessageManagement
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help= "Добавление сообщений через командную строку. Пример: python manage.py add_messages"

    def handle(self, *args, **options):


        # Находим пользователя, например, первого суперпользователя
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(
                self.style.ERROR(
                     "Не найдено ни одного суперпользователя. Сначала создайте его через createsuperuser.")
            )
            return

        message_data = [
            {"message_subject": "ТВ под любой сценарий жизни", "body": "Готовьте, играйте или устраивайте киновечера — телевизоры "
                                                                       " идеально впишутся в ваш ритм жизни."},
            {"message_subject": "Техника для учёбы", "body": "Товары для учёбы и многое другое"},
            {"message_subject": "Обзоры, истории и игры!", "body": "У нас есть много полезных и интересных материалов на самые увлекательные темы."},
            {"message_subject": "Нашли для вас идеальный роутер", "body": "Роутер, который справится со всем. Работаете, учитесь, смотрите кино через интернет — и "
                                                                          "все это порой одновременно? Wi-Fi-роутер позволит справляться со всеми задачами без перебоев и задержек."},
            {"message_subject": "Для всех ввели новую уголовку за банковские переводы", "body": "Узнайте, кому теперь грозит штраф до миллиона и реальный срок"},
        ]

        created_count = 0
        skipped_count = 0

        for data in message_data:
            message, created = MessageManagement.objects.get_or_create(
                message_subject=data["message_subject"], # Уникальный ключ — message_subject
                defaults={# Эти поля будут использованы ТОЛЬКО при создании
                    "body": data["body"],
                    "user": user,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Добавлен: {message.message_subject}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Уже существует: {message.message_subject}")
                )
                skipped_count += 1
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Готово: добавлено {created_count}, пропущено {skipped_count}"
            )
        )

