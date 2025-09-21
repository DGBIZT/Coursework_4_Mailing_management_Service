from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.views import (PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import CustomUser
import uuid
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileUpdateForm
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('customercrm:home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Пользователь неактивен до подтверждения
        user.save()

        self.send_confirmation_email(user)
        return super().form_valid(form)

    def send_confirmation_email(self, user):
        confirmation_link = self.generate_confirmation_link(user)

        send_mail(
            'Подтверждение регистрации',
            f"Пожалуйста, подтвердите свою регистрацию, перейдя по ссылке: {confirmation_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    def generate_confirmation_link(self, user):
        return f"{settings.FRONTEND_URL}/users/confirm/{user.confirmation_token}/"


def confirm_email(request, token):
    try:
        user = CustomUser.objects.get(confirmation_token=token)
        if not user.is_confirmed:
            user.is_active = True
            user.is_confirmed = True
            user.confirmation_token = uuid.uuid4()  # Генерируем новый токен
            user.save()
            return render(request, 'email_confirmed.html', {'message': 'Email подтвержден!'})
        else:
            return render(request, 'email_confirmed.html', {'message': 'Email уже подтвержден'})
    except CustomUser.DoesNotExist:
        return render(request, 'email_confirmed.html', {'message': 'Неверная ссылка'})


def email_confirmed(request):
    return render(request, 'email_confirmed.html', {'message': 'Email подтвержден!'})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Ищем пользователя по email
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('customercrm:home')
                    else:
                        messages.error(request, "Пользователь не активирован")
                else:
                    messages.error(request, "Неверный email или пароль")
            except CustomUser.DoesNotExist:
                messages.error(request, "Пользователь не найден")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Профиль успешно обновлен')
        return response