from django.urls import path
from .views import RegisterView, email_confirmed, confirm_email, CustomPasswordResetView, CustomPasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from .views import ProfileView, ProfileUpdateView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='customercrm:home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-confirmed/', email_confirmed, name='email_confirmed'),
    path('confirm/<uuid:token>/', confirm_email, name='confirm_email'),

    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),

]