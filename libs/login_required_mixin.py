from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Кастомизированный миксин обязательной авторизации"""

    login_url = reverse_lazy('authen:login')
    redirect_field_name = 'redirect_to'
