from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from customer_crm.models import MailingRecipient
from mailing_list.models import  Mailing
from .forms import MailingRecipientFrom
from django.views.generic import TemplateView



class MailingRecipientCreateView(CreateView):
    model = MailingRecipient
    form_class = MailingRecipientFrom
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
    form_class = MailingRecipientFrom
    template_name = 'customer_crm/mailingrecipient_form.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

class MailingRecipientDeleteView(DeleteView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_confirm_delete.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')


class HomeView(TemplateView):
    template_name = 'customer_crm/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Подсчет общего количества рассылок
        context['total_mailings'] = Mailing.objects.count()

        # Подсчет активных рассылок (статус 'Запущена')
        context['active_mailings'] = Mailing.objects.filter(status=Mailing.STARTED).count()

        # Подсчет уникальных получателей
        context['unique_recipients'] = MailingRecipient.objects.count()

        # Последние 5 созданных рассылок для отображения
        # Сортируем по дате начала, если она есть
        recent_mailings = Mailing.objects.order_by('-start_datetime')[:5]

        # Если start_datetime нет, можно использовать id для сортировки
        if not recent_mailings.exists():
            recent_mailings = Mailing.objects.order_by('-id')[:5]

        context['recent_mailings'] = recent_mailings

        return context

