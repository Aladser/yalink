import os
import urllib
from urllib.parse import urlparse

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
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
    """Представление главной страницы"""

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        print(self.request.GET)

        # перенравление на страницу авторизации, если идет запрос на получение содержимого ссылки
        if 'link' in self.request.GET and not request.user.is_authenticated:
            return redirect(reverse("authen:login"))
        if 'type' in self.request.GET:
            return JsonResponse({"response":'Принято'});

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # url строки поиска
        context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""

        if not 'link' in self.request.GET:
            return context

        public_link = context["search_url"] = self.request.GET['link']
        """ссылка на общедоступный Яндекс ресурс"""
        list_api_link = list_api_link_start + urllib.parse.quote(public_link)
        """ссылка на просмотр Яндекс ресурса"""
        download_api_link = general_download_api_link_start + urllib.parse.quote(public_link)
        """ссылка на загрузку Яндекс ресурса"""

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
            context['error'] = "Ссылка не найдена"
            return context
        elif response.status_code == 500:
            context['error'] = "Неправильная ссылка"
            return context
        elif response.status_code != 200:
            context['error'] = "Ошибка. Код ошибки " + str(response.status_code)
            return context

        items_list = get_shared_files_from_public_link(download_api_link, response.json())
        context['types'] = ['Все'] + sorted(list(set(elem['type'] for elem in items_list)))
        context['items'] = items_list
        context['is_items'] = len(items_list) > 0

        return context
