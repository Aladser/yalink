from django.core.management import BaseCommand

from authen.models import User
from libs.seeding import Seeding

# пользователи
user_params_obj_list = [
    {
        'email': 'admin@test.ru',
        'first_name': 'Админ',
        'last_name': 'Админов',
        'is_superuser': True,
        'is_staff': True
    },
    {
        'email': 'user1@test.ru',
        'first_name': 'Пользователь 1',
        'last_name': 'Обычный',
    },
    {
        'email': 'user2@test.ru',
        'first_name': 'Пользователь 2',
        'last_name': 'Обычный',
    },
    {
        'email': 'user3@test.ru',
        'first_name': 'Пользователь 3',
        'last_name': 'Обычный',
    }
]
password = '_strongpassword_'



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # пользователи
        Seeding.seed_users(User, user_params_obj_list, password)
