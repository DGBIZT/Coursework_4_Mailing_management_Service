from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from customer_crm.models import MailingRecipient


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        email = 'testadmin@sky.pro'

        # Проверяем, существует ли уже пользователь
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Пользователь {email} уже существует.'))
            return

        # Создаём пользователя
        user = User.objects.create(
            email=email,
            username=email,  # Обязательно, так как AbstractUser требует username
            first_name='Admin',
            last_name='Admin',
            is_staff=True,
            is_superuser=True,
            is_confirmed=True,  #  Подтверждаем сразу!
        )
        user.set_password('1234')
        user.save()

        # Опционально: добавляем в MailingRecipient, если он должен получать рассылки
        MailingRecipient.objects.get_or_create(
            email=email,
            defaults={
                'full_name': 'Admin Admin',
                'comment': 'Системный администратор'
            }
        )

        self.stdout.write(
            self.style.SUCCESS(f'Администратор успешно создан: {user.email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'is_confirmed = True установлен')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Получатель рассылки добавлен (если не существовал)')
        )