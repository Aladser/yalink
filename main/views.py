import os
import urllib
from urllib.parse import urlparse

import requests
from django.views.generic import TemplateView

from main.services import get_shared_files_from_public_link

element_types = {
    "dir": 'Папка',
    "file": 'Файл'
}
# начало ссылки на просмотр файлов
list_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='
# начало ссылки на скачивание файла
general_download_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='


class MainView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # получение файлов публичной ссылки
        if 'link' in self.request.GET:
            public_link = context["search_url"] = self.request.GET['link']
            # ссылка на просмотр
            list_api_link = list_api_link_start + urllib.parse.quote(public_link)
            # ссылка на загрузку
            download_api_link = general_download_api_link_start + urllib.parse.quote(public_link)

            # проверка корректности ссылки
            public_link_components = urlparse(public_link)
            if public_link_components.netloc != "disk.yandex.ru":
                context['error'] = "Это не ссылка на Яндекс диск"
                return context

            response = requests.get(public_link)
            if response.status_code != 200:
                context['error'] = "Ошибка. Код ошибки " + str(response.status_code)
                return context

            # проверка ссылки просмотра файлов
            response = requests.get(list_api_link)
            if response.status_code == 404:
                context['error'] = "Ссылка на найдена"
                return context
            elif response.status_code == 500:
                context['error'] = "Неправильная ссылка"
                return context
            elif response.status_code != 200:
                context['error'] = "Ошибка. Код ошибки " + str(response.status_code)
                return context

            response_data = response.json()
            items_list = get_shared_files_from_public_link(download_api_link, response_data)
            context['items'] = items_list
            context['is_items'] = len(items_list) > 0
        else:
            context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""

        return context
