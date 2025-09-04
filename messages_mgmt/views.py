from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from messages_mgmt.models import MessageManagement


class MessageManagementCreateView(CreateView):
    model = MessageManagement
    fields = ["message_subject", "body",]
    template_name = 'messages_mgmt/messagemgmt_form.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')

class MessageManagementListView(ListView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemgmt_list.html'
    context_object_name = 'messagemanagements'

class MessageManagementDetailView(DetailView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemanagement_detail.html'
    context_object_name = 'messagemanagement'

class MessageManagementUpdateView(UpdateView):
    model = MessageManagement
    fields = ["message_subject", "body",]
    template_name = 'messages_mgmt/messagemgmt_form.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')

class MessageManagementDeleteView(DeleteView):
    model = MessageManagement
    template_name = 'messages_mgmt/messagemanagement_confirm_delete.html'
    success_url = reverse_lazy('messagesmgmt:messagemgmt_list')