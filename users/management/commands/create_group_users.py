from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Пользователь')

        permissions = Permission.objects.filter(
            codename__in=[
                'add_mailingrecipient',     # создание клиентов
                'view_mailingrecipient',    # просмотр клиентов
                'change_mailingrecipient',  # редактирование клиентов
                'delete_mailingrecipient',  # удаление клиентов
                'add_mailing',      # создание рассылок
                'view_mailing',     # просмотр рассылок
                'change_mailing',   # редактирование рассылок
                'delete_mailing',   # удаление рассылок
                'view_mailing_stats',    # просмотр статистики
            ]
        )

        group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Группа "Пользователь" создана с необходимыми правами.'))
