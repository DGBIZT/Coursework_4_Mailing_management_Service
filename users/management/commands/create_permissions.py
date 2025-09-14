from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(CustomUser)
        permission, created = Permission.objects.get_or_create(
            codename='block_user',
            name='Can block users',
            content_type=content_type
        )
        self.stdout.write(self.style.SUCCESS('Разрешение block_user создано'))