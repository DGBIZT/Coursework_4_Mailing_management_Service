from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_confirmed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        permissions = [
            ('block_user', 'block user'),
        ]

    def block(self):
        """Метод для блокировки пользователя"""
        self.is_blocked = True
        self.save()

    def unblock(self):
        """Метод для разблокировки пользователя"""
        self.is_blocked = False
        self.save()

    def is_active(self):
        """Проверка активности пользователя"""
        return super().is_active and not self.is_blocked

    def has_perm(self, perm, obj=None):
        """Переопределяем проверку прав с учетом блокировки"""
        if self.is_blocked:
            return False
        return super().has_perm(perm, obj)

    def __str__(self):
        return self.email
