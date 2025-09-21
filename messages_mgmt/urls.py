from django.urls import path
from . import views

app_name = 'messages_mgmt'

urlpatterns = [
    path('messagemanagement/create/', views.MessageManagementCreateView.as_view(), name='messagemanagement_create'),
    path('messagemanagement/list/', views.MessageManagementListView.as_view(), name='messagemgmt_list'),
    path('messagemanagement/detail/<int:pk>/', views.MessageManagementDetailView.as_view(), name='messagemanagement_detail'),
    path('messagemanagement/update/<int:pk>/', views.MessageManagementUpdateView.as_view(), name='messagemanagement_update'),
    path('messagemanagement/delete/<int:pk>/', views.MessageManagementDeleteView.as_view(), name='messagemanagement_delete'),

]