from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class MailingListConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailing_list"

    def ready(self):
        # Подключаем сигнал после миграции
        post_migrate.connect(self.create_permissions, sender=self)

    def create_permissions(self, sender, **kwargs):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import AttemptMailing

        try:
            content_type = ContentType.objects.get_for_model(AttemptMailing)

            # Проверяем существование разрешения перед созданием
            try:
                Permission.objects.get(
                    codename='view_mailing_stats',
                    content_type=content_type
                )
            except Permission.DoesNotExist:
                Permission.objects.create(
                    codename='view_mailing_stats',
                    name='Просмотр статистики рассылок',
                    content_type=content_type
                )
        except Exception as e:
            print(f"Ошибка при создании разрешений: {e}")

