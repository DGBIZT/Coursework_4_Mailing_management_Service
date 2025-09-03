from django.urls import path
from . import views

app_name = 'customer_crm'

urlpatterns = [
    path('mailingrecipient/create/', views.MailingRecipientCreateView.as_view(), name='mailingrecipient_create'),
    path('mailingrecipient/list/', views.MailingRecipientListView.as_view(), name='mailingrecipient_list'),
    path('mailingrecipient/detail/<int:pk>/', views.MailingRecipientDetailView.as_view(), name='mailingrecipient_detail'),
    path('mailingrecipient/update/<int:pk>/', views.MailingRecipientUpdateView.as_view(), name='mailingrecipient_update'),
    path('mailingrecipient/delete/<int:pk>/', views.MailingRecipientDeleteView.as_view(), name='mailingrecipient_delete'),


]