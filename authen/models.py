from django.contrib.auth.models import AbstractUser
from django.db import models

from config.settings import NULLABLE


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='почта', unique=True)
    password = models.CharField(verbose_name="password", max_length=128, **NULLABLE)
    phone = models.CharField(verbose_name='телефон', unique=True, max_length=20, **NULLABLE)
    avatar = models.ImageField(verbose_name='аватар', upload_to='images/', **NULLABLE)
    token = models.CharField(verbose_name="Токен", **NULLABLE, max_length=100)
    auth_type = models.CharField(verbose_name="Тип авторизации", default="db")
    yandex_token = models.CharField(verbose_name="Яндекс токен", max_length=255, default=None, **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('first_name', 'last_name', 'email')

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.email
