from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from messages_mgmt.models import MessageManagement
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.utils import timezone
from django.http import Http404
from .forms import MessageManagementForm



class BaseMessageManagementView(LoginRequiredMixin):
    model = MessageManagement

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class MessageManagementCreateView(BaseMessageManagementView, CreateView):
    model = MessageManagement
    form_class = MessageManagementForm
    template_name = 'messages_mgmt/messagemgmt_form.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')

    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.created_at = timezone.now()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Создать'
        return context

class MessageManagementListView(BaseMessageManagementView, ListView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemgmt_list.html'
    context_object_name = 'messagemanagements'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_messages'] = self.get_queryset().count()
        return context

class MessageManagementDetailView(BaseMessageManagementView, DetailView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemanagement_detail.html'
    context_object_name = 'messagemanagement'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("У вас нет прав доступа к этому сообщению")
        return obj

class MessageManagementUpdateView(BaseMessageManagementView, UpdateView):
    model = MessageManagement
    form_class = MessageManagementForm
    template_name = 'messages_mgmt/messagemgmt_form.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("У вас нет прав доступа к этому сообщению")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Редактировать'
        return context

class MessageManagementDeleteView(BaseMessageManagementView, DeleteView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemanagement_confirm_delete.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("У вас нет прав доступа к этому сообщению")
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Проверяем, используется ли сообщение в рассылках
        if self.object.mailing_set.exists():
            messages.error(request, 'Нельзя удалить сообщение, используемое в рассылках')
            return HttpResponseRedirect(success_url)

        self.object.delete()
        messages.success(request, 'Сообщение успешно удалено')
        return HttpResponseRedirect(success_url)