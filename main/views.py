import os
import urllib
from urllib.parse import urlparse

import requests
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from libs.managed_cache import ManagedCache
from main.services import get_elements_of_public_link

element_types = {
    "dir": 'Папка',
    "file": 'Файл'
}
# начало ссылки на просмотр файлов
list_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='

class MainView(TemplateView):
    """Представление главной страницы"""

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        # перенаправление на страницу авторизации, если идет запрос на получение содержимого ссылки без авторизации
        if 'link' in self.request.GET and not request.user.is_authenticated:
            return redirect(reverse("authen:login"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""
        if not 'link' in self.request.GET:
            return context

        public_link = cache_key = context["search_url"] = self.request.GET['link']
        """ссылка на общедоступный Яндекс ресурс"""
        # проверка корректности ссылки
        public_link_components = urlparse(public_link)
        print(public_link_components)
        if public_link_components.netloc not in ('yadi.sk', 'disk.yandex.ru') or public_link_components.path.split('/')[1] != 'd':
            context['error'] = "Не публичная ссылка на Яндекс диск"
            return context

        list_api_link = list_api_link_start + urllib.parse.quote(public_link)
        """ссылка на просмотр содержимого публичной яндекс ссылки"""
        # если открывается внутренняя папка ссылки
        if 'path' in  self.request.GET:
            list_api_link += f"&path={urllib.parse.quote(self.request.GET['path'])}"
            cache_key += self.request.GET['path']

        # --- Получение из КЭШа ---
        cached_data = ManagedCache.get_data(cache_key)
        if cached_data:
            context['items'], context['types'] = cached_data['items'], cached_data['types']
            context['is_items'] = len(context['items']) > 0
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

        items_list = get_elements_of_public_link(public_link, response.json())
        context['types'] = ['Все'] + sorted(list(set(elem['type'] for elem in items_list)))
        context['items'] = items_list
        context['is_items'] = len(items_list) > 0
        ManagedCache.save_data(cache_key, {"items": items_list, "types": context['types']})

        return context
