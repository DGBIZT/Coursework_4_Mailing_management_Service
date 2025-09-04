from django.contrib import admin
from .models import Mailing

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):

    # создаем метод для отображения получателей

    def get_recipients(self, obj):
        return ", ".join([recipient.name for recipient in obj.recipients.all()])

    get_recipients.short_description = "Получатели"

    list_display = ('start_datetime', 'end_datetime', 'status', 'message','get_recipients')
    list_filter = ('status',)
    search_fields = ('start_datetime', 'end_datetime', 'status', 'message', 'get_recipients',)
