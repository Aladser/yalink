from django.contrib.auth.views import LogoutView
from django.urls import path
from authen.apps import AuthenConfig
from authen.views import *
from django.contrib.auth import views as auth_views

app_name = AuthenConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register-complete/', RegisterCompleteView.as_view(), name='register-complete'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('email-confirm/<str:token>/', VerificateEmailView.as_view(), name='email-confirm'),

    path('password-reset/', CustomPasswordResetView.as_view(), name='password-reset'),
    path('password_reset_confirm/<uidb64>/<token>/', CustomUserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', CustomPasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
]
