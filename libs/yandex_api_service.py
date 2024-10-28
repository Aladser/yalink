import os
import urllib
import requests
from requests_oauthlib import OAuth2Session
from urllib.parse import urlparse
from authen.models import User


class YandexAPIService:
    """Работа с API Яндекс"""

    default_avatar_codeword = "DEFAULT_AVATAR_ID"
    element_types = {
        "dir": 'Папка',
        "file": 'Файл'
    }

    YANDEX_CLIENT_ID = os.getenv("ClientID")
    YANDEX_CLIENT_SECRET = os.getenv("ClientSecret")
    YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"

    list_api_url_start = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='
    """начало ссылки на просмотр файлов"""
    general_download_api_url_start = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='
    """начало ссылки на скачивание файла"""
    userinfo_url = "https://login.yandex.ru/info"
    """Ссылка на получение информации о пользователе"""
    avatar_url = f"https://avatars.yandex.net/get-yapic/{default_avatar_codeword}/islands-200"
    """Ссылка на получение аватара пользователя"""

    @staticmethod
    def get_authorization_url():
        """Возвращает ссылку на авторизацию"""
        oauth = OAuth2Session(client_id=YandexAPIService.YANDEX_CLIENT_ID)
        authorization_url, state = oauth.authorization_url(YandexAPIService.YANDEX_AUTH_URL, force_confirm="true")
        return authorization_url

    @staticmethod
    def get_access_token(code: str) -> str:
        """Возвращает токен доступа"""
        oauth = OAuth2Session(client_id=YandexAPIService.YANDEX_CLIENT_ID)
        return oauth.fetch_token(
            token_url=YandexAPIService.YANDEX_TOKEN_URL,
            code=code,
            client_secret=YandexAPIService.YANDEX_CLIENT_SECRET
        )["access_token"]

    @staticmethod
    def get_elements_of_yadisk_public_link(public_link: str, path: str | None = None) -> dict:
        """
        Возвращает список папок и файлов публичной ссылки Яндекс Диска
        :param public_link: публичная ссылка
        :param path: относительный путь элемента ссылки
        :return: {код ответа, данные}
        """

        decoded_public_link = urllib.parse.quote(public_link)
        list_api_link = YandexAPIService.list_api_url_start + decoded_public_link
        """ссылка на просмотр содержимого"""
        if path:
            list_api_link += f"&path={path}"
        download_api_link = YandexAPIService.general_download_api_url_start + decoded_public_link
        """ссылка на загрузку"""

        # проверка ссылки просмотра файлов
        response = requests.get(list_api_link)
        if response.status_code == 404:
            return {'code': response.status_code, "data": "Ссылка не найдена"}
        elif response.status_code == 500:
            return {'code': response.status_code, "data": "Неправильная ссылка"}
        elif response.status_code != 200:
            return {'code': response.status_code, "data": f"Ошибка. Код ошибки {str(response.status_code)}"}

        items_list = []
        response_data = response.json()
        if response_data.get('type') == 'file':
            # открывается публичный файл
            items_list.append({'name': response_data.get('name'), 'url': response_data.get('file')})
        else:
            # открывается публичная папка
            items = response_data.get('_embedded', {}).get('items', [])
            for item in items:
                elem_name = f"{YandexAPIService.element_types[item['type']]} {item['name']}"

                if item['type'] == 'file':
                    get_elem_download_url = f"{download_api_link}&path={item['path']}"
                    get_elem_download_url_data = requests.get(get_elem_download_url)
                    elem_link = get_elem_download_url_data.json()['href']
                    elem_type = item.get('media_type')
                else:
                    elem_link = '/?link=' + public_link + '&path=' + urllib.parse.quote(item['path'])
                    elem_type = 'Папка'
                items_list.append({'name': elem_name, 'url': elem_link, 'type': elem_type})

        return {'code': 200, "data": items_list}

    @staticmethod
    def get_yadisk_resource_download_link(public_link: str) -> str | None:
        """
        Возвращает ссылку на скачивание публичной ссылки Яндекс Диска
        """
        decoded_public_link = urllib.parse.quote(public_link)
        download_link = YandexAPIService.general_download_api_url_start + decoded_public_link
        download_link_request_response = requests.get(download_link)
        return download_link_request_response.json()['href']

    @staticmethod
    def get_userinfo(access_token: str) -> dict:
        """
        Возвращает информацию о пользователе
        :param access_token: токен доступа
        """

        headers = {'Authorization': f'OAuth {access_token}'}
        user_info = requests.get(YandexAPIService.userinfo_url, headers=headers).json()

        default_avatar_id = user_info.get('default_avatar_id')
        avatar_url = YandexAPIService.avatar_url.replace(YandexAPIService.default_avatar_codeword, default_avatar_id)
        user_info['avatar_url'] = avatar_url
        return user_info

    @staticmethod
    def get_or_create_user(user_info: dict, access_token: str) -> User:
        """
        Возвращает или создает Яндекс пользователя в БД
        :param user_info: данные о пользователе
        :param access_token: токен доступа
        """

        email = user_info['login'] + "@yandex.ru"

        user = User.objects.filter(email=email)
        if user.exists():
            user = user.first()
        else:
            user = User()
            user.email = email

        if user.avatar != user_info['avatar_url']:
            user.avatar = user_info['avatar_url']
        if user.first_name != user_info['first_name']:
            user.first_name = user_info['first_name']
        if user.last_name != user_info['last_name']:
            user.last_name = user_info['last_name']
        user.yandex_token = access_token
        user.auth_type = 'yandex'

        user.save()
        return user

    @staticmethod
    def is_valid_public_url(url:str) -> False:
        """
        Проверяет корректность ссылки
        """

        public_link_components = urlparse(url)
        if public_link_components.netloc not in ('yadi.sk', 'disk.yandex.ru') or public_link_components.path.split('/')[1] != 'd':
            return False
        return True
