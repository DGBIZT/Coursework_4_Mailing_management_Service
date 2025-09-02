from django.contrib import admin
from .models import MailingRecipient

@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment')
    list_filter = ('email', 'full_name')
    search_fields = ('email', 'full_name', 'comment')
