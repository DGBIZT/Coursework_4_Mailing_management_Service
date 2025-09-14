from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from customer_crm.models import MailingRecipient
from mailing_list.models import  Mailing
from .forms import MailingRecipientFrom
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import HttpResponseForbidden
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache



class BaseCustomerCRMView(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class MailingRecipientCreateView(BaseCustomerCRMView, CreateView):
    model = MailingRecipient
    form_class = MailingRecipientFrom
    template_name = 'customer_crm/mailingrecipient_form.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Устанавливаем связь с пользователем
        return super().form_valid(form)

@method_decorator(cache_page(60 * 5), name='dispatch')
class MailingRecipientListView(BaseCustomerCRMView, ListView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_list.html'
    context_object_name = 'mailingrecipients'

    def get_queryset(self):
        return MailingRecipient.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MailingRecipientFrom(user=self.request.user)
        return context

@method_decorator(cache_page(60 * 5), name='dispatch')
class MailingRecipientDetailView(BaseCustomerCRMView,DetailView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_detail.html'
    context_object_name = 'mailingrecipient'

class MailingRecipientUpdateView(BaseCustomerCRMView, UpdateView):
    model = MailingRecipient
    form_class = MailingRecipientFrom
    template_name = 'customer_crm/mailingrecipient_form.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Вы не имеете доступа к этому объекту")
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if form.instance.user != self.request.user:
            return HttpResponseForbidden("Доступ запрещен")
        return super().form_valid(form)

class MailingRecipientDeleteView(BaseCustomerCRMView, DeleteView):
    model = MailingRecipient
    template_name = 'customer_crm/mailingrecipient_confirm_delete.html'
    success_url = reverse_lazy('customercrm:mailingrecipient_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Вы не имеете доступа к этому объекту")
        return obj

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user:
            return HttpResponseForbidden("Доступ запрещен")
        return super().dispatch(request, *args, **kwargs)


class HomeView(BaseCustomerCRMView, TemplateView):
    template_name = 'customer_crm/home.html'

    # @method_decorator(cache_page(60 * 5))  # Кеширование на 5 минут
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Подсчет общего количества рассылок
        context['total_mailings'] = Mailing.objects.filter(user=user).count()

        # Подсчет активных рассылок (статус 'Запущена')
        context['active_mailings'] = Mailing.objects.filter(
            user=user,
            status=Mailing.STARTED
        ).count()

        # Подсчет уникальных получателей
        context['unique_recipients'] = MailingRecipient.objects.filter(
            user=user
        ).count()

        # Последние 5 созданных рассылок для отображения
        # Сортируем по дате начала, если она есть
        recent_mailings = Mailing.objects.filter(
            user=user
        ).order_by('-start_datetime')[:5]

        # Если start_datetime нет, можно использовать id для сортировки
        if not recent_mailings.exists():
            recent_mailings = Mailing.objects.filter(
                user=user
            ).order_by('-id')[:5]

        context['recent_mailings'] = recent_mailings

        return context

