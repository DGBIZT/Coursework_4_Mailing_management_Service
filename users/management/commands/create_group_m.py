from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджер')

        permissions = Permission.objects.filter(
            codename__in=[
                'view_mailingrecipient',  # просмотр клиентов
                'view_mailing',  # просмотр рассылок
                'view_customuser',  # просмотр списка пользователей
                'block_user',  # блокировка пользователей
                'disable_mailing',  # отключение рассылок
            ]
        )
        group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Группа "Менеджер" создана с необходимыми правами.'))






