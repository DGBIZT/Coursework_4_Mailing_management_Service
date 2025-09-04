from django.urls import path
from . import views

app_name = 'mailing_list'

urlpatterns = [
    path('mailing/create/', views.MailingCreate.as_view(), name='mailing_create'),
    path('mailing/list/', views.MailingList.as_view(), name='mailing_list'),
    path('mailing/detail/<int:pk>/', views.MailingDetail.as_view(), name='mailing_detail'),
    path('mailing/update/<int:pk>/', views.MailingUpdate.as_view(), name='mailing_update'),
    path('mailing/delete/<int:pk>/', views.MailingDelete.as_view(), name='mailing_delete'),
]