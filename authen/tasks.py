import os

from celery import shared_task
from django.core.mail import send_mail

from config.settings import APP_NAME, EMAIL_HOST_USER


@shared_task
def send_email(email, token) -> str:
    """Отправляет отложенно сообщение на электронную почту пользователя"""

    url = f"{os.getenv('SITE_ADDR')}/user/email-confirm/{token}"
    response = send_mail(
        "Подтвердите свою почту",
        f"Пройдите по ссылке {url} для подтверждения регистрации на сайте {APP_NAME}",
        EMAIL_HOST_USER,
        (email,),
        fail_silently=True
    )
    return "Отправлено" if response else response
