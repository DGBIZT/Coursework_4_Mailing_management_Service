from django.urls import path
from . import views

app_name = 'messages_mgmt'

urlpatterns = [
    path('messagemanagement/create/', views.MessageManagementCreateView.as_view(), name='messagemanagement_create'),
    path('messagemanagement/list/', views.MessageManagementListView.as_view(), name='messagemanagement_list'),


    path('mailingrecipient/detail/<int:pk>/', views.MailingRecipientDetailView.as_view(), name='mailingrecipient_detail'),
    path('mailingrecipient/update/<int:pk>/', views.MailingRecipientUpdateView.as_view(), name='mailingrecipient_update'),
    path('mailingrecipient/delete/<int:pk>/', views.MailingRecipientDeleteView.as_view(), name='mailingrecipient_delete'),
]