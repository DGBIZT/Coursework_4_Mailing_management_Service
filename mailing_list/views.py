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
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect


User = get_user_model()

class BaseMailingView(LoginRequiredMixin):
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class MailingList(BaseMailingView, ListView):
    model = Mailing
    template_name = 'mailing_list/mailing_list.html'
    context_object_name = 'mailings_list'

    def get_queryset(self):
        return Mailing.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['mailings_list'] = Mailing.objects.all()  # Явное указание queryset
        return context

class MailingCreate(BaseMailingView, CreateView):
    model = Mailing
    form_class = CompleteMailingForm
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  # Привязываем рассылку к пользователю
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_messages'] = MessageManagement.objects.filter(user=self.request.user)
        return context

class MailingDetail(BaseMailingView, DetailView):
    model = Mailing
    template_name = 'mailing_list/mailing_detail.html'
    context_object_name = 'mailing_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = AttemptMailing.objects.filter(
            mailing=self.object,
            mailing__user=self.request.user
        )
        return context

class MailingUpdate(BaseMailingView, UpdateView):
    model = Mailing
    form_class = CompleteMailingForm
    template_name = 'mailing_list/mailing_form.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем пользователя в форму
        return kwargs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Вы не имеете доступа к этой рассылке")
        return obj

    # def get_queryset(self):
    #     return Mailing.objects.filter(
    #         user=self.request.user,
    #         status=Mailing.CREATED  # Возможно, добавить фильтрацию по статусу
    #     )


class MailingDelete(BaseMailingView, DeleteView):
    model = Mailing
    template_name = 'mailing_list/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailinglist:mailing_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Вы не имеете доступа к этой рассылке")
        return obj


class MailingSend(BaseMailingView, SingleObjectMixin, View):
    model = Mailing

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        mailing = self.get_object()

        if mailing.user != self.request.user:
            raise Http404("Вы не имеете доступа к этой рассылке")

        message = mailing.message
        subject = message.message_subject
        body = message.body
        sender_email = settings.DEFAULT_FROM_EMAIL
        recipients = [recipient.email for recipient in mailing.recipients.all()]

        try:
            # Отправляем сообщение
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
                status=AttemptMailing.SUCCESS,
                user=self.request.user
            )
            attempt.mail_server_response = f"Отправлено {response} писем"
            attempt.save()

            messages.success(request, 'Сообщение успешно отправлено')
            return HttpResponseRedirect(reverse_lazy(
                'mailing_list:mailing_detail',
                kwargs={'pk': mailing.pk}
            ))

        except Exception as e:
            # Обновляем статус в случае ошибки
            mailing.status = Mailing.FAILED
            mailing.save()

            # Создаем запись об ошибке
            attempt = AttemptMailing.objects.create(
                mailing=mailing,
                status=AttemptMailing.FAILURE,
                user=self.request.user
            )
            attempt.mail_server_response = str(e)
            attempt.save()

            messages.error(request, f'Ошибка при отправке: {str(e)}')
            return HttpResponseRedirect(reverse_lazy(
                'mailing_list:mailing_detail',
                kwargs={'pk': mailing.pk}
            ))


class CompleteMailing(BaseMailingView, View):
    def post(self, request, pk):
        # mailing = Mailing.objects.get(pk=pk)
        try:
            # Получаем объект рассылки с проверкой существования
            mailing = get_object_or_404(Mailing, pk=pk)

            # Проверяем права доступа
            if mailing.user != request.user:
                raise Http404("Рассылка не найдена или у вас нет прав доступа")

            # Проверяем текущий статус рассылки
            if mailing.status == Mailing.COMPLETED:
                messages.error(request, 'Рассылка уже завершена')
                return redirect('mailing_list:mailing_detail', pk=pk)

            # Обновляем статус и время завершения
            mailing.status = Mailing.COMPLETED
            mailing.completed_at = timezone.now()
            mailing.save()

            messages.success(request, 'Рассылка успешно завершена')
            return redirect('mailing_list:mailing_detail', pk=pk)

        except Mailing.DoesNotExist:
            raise Http404("Рассылка не найдена")
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
            return redirect('mailing_list:mailing_detail', pk=pk)


class StatsView(LoginRequiredMixin, View):

    @method_decorator(permission_required('mailing_list.view_mailing_stats', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    permission_required = 'mailing_list.view_mailing_stats'
    login_url = '/login/'

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
