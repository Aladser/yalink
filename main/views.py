import os

from django.views.generic import TemplateView
import requests
import urllib

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
            # проверка корректности ссылки
            public_link = context["search_url"] = self.request.GET['link']
            response = requests.get(public_link)
            if response.status_code != 200:
                context['error'] = response.status_code
                print(response.__dict__)
                return context


            # ссылка на просмотр
            list_api_link = list_api_link_start + urllib.parse.quote(public_link)
            # проверка ссылки просмотра файлов
            response = requests.get(list_api_link)
            if response.status_code != 200:
                context['error'] = response.status_code
                print(response.__dict__)
                return context

            # ссылка на загрузку
            download_api_link = general_download_api_link_start + urllib.parse.quote(public_link)
            response_data = response.json()
            items_list = get_shared_files_from_public_link(download_api_link, response_data)
            context['items'] = items_list
            context['is_items'] = len(items_list) > 0
        else:
            context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""

        return context
