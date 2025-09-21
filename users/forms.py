from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.forms import ClearableFileInput




class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш телефон'
        }),
        help_text='Необязательное поле. Введите ваш номер телефона.'
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пароль'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль'
            })
        }
        labels = {
            'email': 'Email',
            'username': 'Имя пользователя',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'phone_number': 'Телефон',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля'
        }
        help_texts = {
            'password1': 'Пароль должен содержать минимум 8 символов',
            'password2': 'Повторите введенный пароль'
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise ValidationError('Номер телефона должен содержать только цифры.')
        return phone_number


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                if not user.is_active:
                    raise ValidationError("Пользователь не активирован")
            except CustomUser.DoesNotExist:
                raise ValidationError("Пользователь не найден")
        return self.cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш email'
        }),
        label='Email'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()

        # Проверяем существование пользователя
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email не найден")

        # Проверяем, что пользователь не заблокирован
        if User.objects.filter(email=email, is_blocked=True).exists():
            raise ValidationError("Пользователь заблокирован")

        return email

    def get_users(self, email):
        """Переопределяем метод для игнорирования is_active"""
        User = get_user_model()
        return User.objects.filter(email__iexact=email, is_blocked=False)


class ProfileUpdateForm(UserChangeForm):
    password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'avatar']
        widgets = {
            'avatar': ClearableFileInput(attrs={'multiple': False}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
