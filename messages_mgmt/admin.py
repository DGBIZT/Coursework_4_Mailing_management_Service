from django.contrib import admin
from .models import MessageManagement

@admin.register(MessageManagement)
class MessageManagement(admin.ModelAdmin):
    list_display = ('message_subject', 'body',)
    list_filter = ('message_subject', 'body',)
    search_fields = ('message_subject', 'body',)
