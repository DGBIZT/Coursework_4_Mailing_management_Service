from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from customer_crm.models import MailingRecipient


class MailingRecipientCreateView(CreateView):
    model = MailingRecipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'customer_crm/mailingrecipient_form.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

class MailingRecipientListView(ListView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_list.html'
    context_object_name = 'mailingrecipients'

class MailingRecipientDetailView(DetailView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_detail.html'
    context_object_name = 'mailingrecipient'

class MailingRecipientUpdateView(UpdateView):
    model = MailingRecipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'customer_crm/mailingrecipient_form.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

class MailingRecipientDeleteView(DeleteView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_confirm_delete.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')