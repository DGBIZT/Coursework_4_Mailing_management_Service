from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Права доступа', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_confirmed', 'is_blocked')
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Определяем, какие поля доступны для редактирования
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Менеджер').exists():
            return (
                'username', 'password', 'first_name', 'last_name', 'email',
                'phone_number', 'is_staff', 'is_superuser',
                'groups', 'user_permissions', 'last_login', 'date_joined',
                'is_confirmed'
            )
        return super().get_readonly_fields(request, obj)

    # Определяем, какие поля доступны для изменения
    def get_fieldsets(self, request, obj=None):
        if request.user.groups.filter(name='Менеджер').exists():
            return (
                (None, {'fields': ('username', 'password')}),
                ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
                ('Права доступа', {'fields': ('is_staff', 'is_superuser', 'is_confirmed', 'is_blocked')}),
                ('Важные даты', {'fields': ('last_login', 'date_joined')}),
            )
        return super().get_fieldsets(request, obj)

    # Настраиваем список отображения
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_confirmed', 'is_staff', 'is_superuser', 'is_blocked'
    )

    # Настраиваем фильтрацию
    list_filter = ('is_confirmed', 'is_staff', 'is_superuser', 'is_blocked')

    # Определяем доступные действия
    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Менеджер').exists():
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(CustomUser, CustomUserAdmin)
