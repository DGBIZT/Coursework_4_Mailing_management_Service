from django.urls import path
from .views import RegisterView
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='customercrm:home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]