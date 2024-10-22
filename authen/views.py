import os
from secrets import token_hex
from urllib.request import Request

from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from requests_oauthlib import OAuth2Session

from authen.forms import RegisterForm, AuthForm, ProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
from authen.models import User
from authen.services import verificate_user
from authen.tasks import send_email
from libs.authen_mixin import AuthenMixin

YANDEX_CLIENT_ID = os.getenv("ClientID")
YANDEX_CLIENT_SECRET = os.getenv("ClientSecret")
YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"


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

        # ссылка яндекс-авторизации
        oauth = OAuth2Session(client_id=YANDEX_CLIENT_ID)
        context['authorization_url'], state = oauth.authorization_url(YANDEX_AUTH_URL, force_confirm="true")

        return context


# АВТОРИЗАЦИЯ ЧЕРЕЗ ЯНДЕКС
def yalogin(request: Request)->HttpResponseRedirect:
    email = request.GET['cid'] + "@yandex.ru"

    oauth = OAuth2Session(client_id=YANDEX_CLIENT_ID)
    token = oauth.fetch_token(
        token_url=YANDEX_TOKEN_URL,
        code=request.GET['code'],
        client_secret=YANDEX_CLIENT_SECRET
    )

    # поиск пользователя
    user = User.objects.filter(email=email)
    if user.exists():
        user = user.first()
    else:
        user = User()
        user.email = email

    user.yandex_token = token["access_token"]
    user.save()
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
