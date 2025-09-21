# admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Mailing


class MailingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_message_subject',
        'start_datetime',
        'status',
        'user',
        'is_active'
    )

    list_filter = ('status', 'start_datetime')
    search_fields = ('message__message_subject', 'message__body')

    # Метод для отображения темы сообщения
    def get_message_subject(self, obj):
        # Исправленный синтаксис среза строки
        return obj.message.message_subject[:50]  # добавили квадратные скобки

    get_message_subject.short_description = _('Тема сообщения')

    # Поле активности
    def is_active(self, obj):
        return obj.status != Mailing.COMPLETED

    is_active.boolean = True
    is_active.short_description = _('Активна')

    # Определяем доступные для редактирования поля
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return ()
        if request.user.groups.filter(name='Менеджер').exists():
            return (
                'message',
                'start_datetime',
                'end_datetime',
                'user',
                'recipients'
            )
        return ()

    # Настраиваем доступные поля для изменения
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return super().get_fieldsets(request, obj)
        if request.user.groups.filter(name='Менеджер').exists():
            return (
                (None, {
                    'fields': ('status',)  # Поле для управления статусом
                }),
            )
        return super().get_fieldsets(request, obj)

    # Определяем права доступа
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name='Менеджер').exists():
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_staff


admin.site.register(Mailing, MailingAdmin)
