from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Mailing, AttemptMailing
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from .forms import CompleteMailingForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User
from messages_mgmt.models import MessageManagement
from django.contrib.auth import get_user_model


User = get_user_model()

class MailingList(ListView):
    model = Mailing
    template_name = 'mailing_list/mailing_list.html'
    context_object_name = 'mailings_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailings_list'] = Mailing.objects.all()  # Явное указание queryset
        return context

class MailingCreate(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ["message", "recipients",]
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

class MailingDetail(DetailView):
    model = Mailing
    template_name = 'mailing_list/mailing_detail.html'
    context_object_name = 'mailing_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = AttemptMailing.objects.filter(mailing=self.object)
        return context

class MailingUpdate(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ["status", "message", "message", "recipients",]
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

class MailingDelete(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing_list/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

class MailingSend(LoginRequiredMixin, SingleObjectMixin, View):
    model = Mailing

    def post(self, request, *args, **kwargs):
        # Получаем объект рассылки
        self.object = self.get_object()
        mailing = self.get_object()

        # Получаем сообщение из связанной модели MessageManagement
        message = mailing.message

        # Формируем данные для отправки
        subject = message.message_subject
        body = message.body
        sender_email = settings.DEFAULT_FROM_EMAIL

        # Получаем список получателей
        recipients = [recipient.email for recipient in mailing.recipients.all()]

        try:
            # Отправляем сообщение
            # Получаем ответ от почтового сервера
            response = send_mail(
                subject,
                body,
                sender_email,
                recipients,
                fail_silently=False
            )

            # Обновляем статус рассылки
            mailing.status = Mailing.STARTED
            mailing.save()

            # Создаем попытку отправки
            attempt = AttemptMailing.objects.create(
                mailing=mailing,
                status=AttemptMailing.SUCCESS
            )
            # Сохраняем реальный ответ сервера

            attempt.mail_server_response = f"Отправлено {response} писем"
            attempt.save()

            # mailing.status = Mailing.COMPLETED
            # mailing.save()

            # Показываем сообщение об успехе
            messages.success(request, 'Сообщение успешно отправлено')
            return HttpResponseRedirect(reverse_lazy('mailing_list:mailing_detail', kwargs={'pk': mailing.pk}))

        except Exception as e:
            mailing.status = Mailing.STARTED
            mailing.save()
            # Создаем запись об ошибке
            attempt = AttemptMailing.objects.create(
                mailing=mailing,
                status=AttemptMailing.FAILURE
            )
            attempt.mail_server_response = str(e)
            attempt.save()
            messages.error(request, f'Ошибка при отправке: {str(e)}')
            return HttpResponseRedirect(reverse_lazy('mailing_list:mailing_detail', kwargs={'pk': mailing.pk}))


class CompleteMailing(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = Mailing.objects.get(pk=pk)

        # Проверяем, что рассылка не уже завершена
        if mailing.status == Mailing.COMPLETED:
            messages.error(request, 'Рассылка уже завершена')
            return HttpResponseRedirect(reverse_lazy('mailing_list:mailing_detail', kwargs={'pk': pk}))

        # Меняем статус на завершенный
        mailing.status = Mailing.COMPLETED
        mailing.save()

        messages.success(request, 'Рассылка успешно завершена')
        return HttpResponseRedirect(reverse_lazy('mailing_list:mailing_detail', kwargs={'pk': pk}))


class StatsView(View):
    def get(self, request):
        user = request.user

        # Получаем все сообщения пользователя
        user_messages = MessageManagement.objects.filter(user=user)

        # Получаем все рассылки через связанные сообщения
        mailings = Mailing.objects.filter(message__in=user_messages)

        # Проверяем, есть ли рассылки у пользователя
        if not mailings.exists():
            return render(request, 'mailing_list/stats.html', {'no_data': True})

        # Подсчет статистики
        stats = {
            'total_attempts': AttemptMailing.objects.filter(
                mailing__in=mailings
            ).count(),

            'success_attempts': AttemptMailing.objects.filter(
                mailing__in=mailings,
                status=AttemptMailing.SUCCESS
            ).count(),

            'failed_attempts': AttemptMailing.objects.filter(
                mailing__in=mailings,
                status=AttemptMailing.FAILURE
            ).count(),
        }

        # Получаем последние попытки
        recent_attempts = AttemptMailing.objects.filter(
            mailing__in=mailings
        ).order_by('-time_attempt')[:10]

        return render(
            request,
            'mailing_list/stats.html',
            {
                'stats': stats,
                'recent_attempts': recent_attempts,
                'success_rate': (
                    stats['success_attempts'] /
                    stats['total_attempts'] * 100
                    if stats['total_attempts'] > 0 else 0
                ),
                'AttemptMailing': AttemptMailing
            }
        )
