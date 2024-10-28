from secrets import token_hex
from urllib.request import Request

from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, PasswordResetCompleteView, INTERNAL_RESET_SESSION_TOKEN
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView

from authen.forms import RegisterForm, AuthForm, ProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
from authen.models import User
from authen.services import verificate_user
from authen.tasks import send_email
from libs.authen_mixin import AuthenMixin
from libs.yandex_api_service import YandexAPIService


# АВТОРИЗАЦИЯ
class UserLoginView(AuthenMixin, LoginView):
    extra_context = {
        'title': "авторизация",
        'header': "Авторизация пользователя",
    }
    template_name = 'login.html'
    form_class = AuthForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['authorization_url'] = YandexAPIService.get_authorization_url()
        return context

# АВТОРИЗАЦИЯ ЧЕРЕЗ ЯНДЕКС
def yalogin(request: Request)->HttpResponseRedirect:
    access_token = YandexAPIService.get_access_token(request.GET['code'])
    user_info = YandexAPIService.get_userinfo(access_token)
    user = YandexAPIService.get_or_create_user(user_info, access_token)
    auth_login(request, user)

    return HttpResponseRedirect('/')

# РЕГИСТРАЦИЯ
class RegisterView(AuthenMixin, CreateView):
    extra_context = {
        'title': "регистрация",
        'header': "Регистрация пользователя",
    }

    model = User
    form_class = RegisterForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('authen:login')

    def form_valid(self, form):
        if form.is_valid():
            # создание ссылки подтверждения почты
            self.object = form.save()
            self.object.is_active = False
            self.object.token = token_hex(10)
            self.object.save()
            send_email.delay(self.object.email, self.object.token)
            return redirect(reverse_lazy("authen:register-complete"))

        return super().form_valid(form)


# ПРОФИЛЬ
class ProfileView(AuthenMixin, UpdateView):
    title = "профиль  пользователя"
    extra_context = {
        'title': title,
        'header': title.capitalize(),
    }

    model = User
    form_class = ProfileForm
    template_name = 'user_form.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user


# СБРОС ПАРОЛЯ - ОТПРАВКА ССЫЛКИ НА ПОЧТУ
class CustomPasswordResetView(PasswordResetView):
    title = "сброс пароля"
    extra_context = {
        'title': title,
        'header': title.capitalize(),
    }

    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('authen:password_reset_done')

# СБРОС ПАРОЛЯ - ВВОД НОВОГО ПАРОЛЯ
class CustomUserPasswordResetConfirmView(PasswordResetConfirmView):
    title = "ввод нового пароля"
    extra_context = {
        'title': title,
        'header': title.capitalize(),
    }

    template_name = 'password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('authen:password_reset_complete')

    def form_valid(self, form):
        # переключение авторизации, если была не db
        user = form.save()
        if user != 'db':
            user.auth_type = 'db'
            user.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return HttpResponseRedirect(self.get_success_url())

# СБРОС ПАРОЛЯ - ПРОВЕРКА ВВОДА НОВОГО ПАРОЛЯ
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    title = "ввод нового пароля"
    extra_context = {
        'title': title,
        'header': title.capitalize(),
    }

# ПОДТВЕРЖДЕНИЕ ПОЧТЫ
class VerificateEmailView(TemplateView):
    extra_context = {
        'title': "подтверждение регистрации",
    }
    template_name = "verification_complete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        if kwargs.get('token'):
            context['description'] = verificate_user(kwargs['token'])
        return context


# ЗАВЕРШЕНИЕ РЕГИСТРАЦИИ
class RegisterCompleteView(TemplateView):
    extra_context = {
        'title': "регистрация пользователя",
    }

    template_name = "register_complete.html"
