from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Mailing

class MailingList(ListView):
    model = Mailing
    template_name = 'mailing_list/mailing_list.html'
    context_object_name = 'mailings_list'

class MailingCreate(CreateView):
    model = Mailing
    fields = ["message", "recipients",]
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

class MailingDetail(DetailView):
    model = Mailing
    template_name = 'mailing_list/mailing_detail.html'
    context_object_name = 'mailing_list'

class MailingUpdate(UpdateView):
    model = Mailing
    fields = ["status", "message", "message", "recipients",]
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

class MailingDelete(DeleteView):
    model = Mailing
    template_name = 'mailing_list/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailinglist:mailing_list')