import os

from django.views.generic import TemplateView
import requests
import urllib

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
            # ссылка на загрузку
            download_api_link = general_download_api_link_start + urllib.parse.quote(public_link)

            # проверка ссылки просмотра файлов
            response = requests.get(list_api_link)
            if response.status_code != 200:
                context['error'] = response.status_code
                print(response.__dict__)
                return context

            items_list = []
            if response.json()['type'] == 'file':
                # открывается публичный файл

                item = response.json()
                items_list.append({'name': item['name'], 'url': item['file']})
            else:
                # открывается публичная папка

                items = response.json().get('_embedded', {}).get('items', [])
                for item in items:
                    elem_name = f"{element_types[item['type']]} {item['name']}"

                    get_elem_download_url = f"{download_api_link}&path={item['path']}"
                    get_elem_download_url_data = requests.get(get_elem_download_url)
                    download_link = get_elem_download_url_data.json()['href']
                    items_list.append({'name': elem_name, 'url': download_link})

            context['items'] = items_list
            context['is_items'] = len(items_list) > 0
        else:
            context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""

        return context
