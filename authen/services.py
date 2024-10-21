from authen.models import User


def verificate_user(token: str) -> str:
    """Проверяет токен регистрации пользователя"""

    if User.objects.filter(token=token).exists():
        user = User.objects.get(token=token)
        user.is_active = True
        user.token = None
        user.save()

        return 'Почта успешно подтверждена'
    else:
        return 'Ссылка недействительная'
