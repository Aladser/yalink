from django.views.generic import TemplateView
import requests
import urllib

class MainView(TemplateView):
    extra_context = {
    }
    template_name = 'index.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        # получение файлов публичной ссылки
        if 'link' in self.request.GET:
            public_link = self.request.GET['link']
            response = requests.get(public_link)
            print(response)

            # Ссылка на скачивание
            download_api_link = 'https://cloud-api.yandex.net/v1/disk/public/resources/download' + '?public_key=' + urllib.parse.quote(public_link)
            # ссылка на просмотр
            list_api_link = 'https://cloud-api.yandex.net/v1/disk/public/resources' + '?public_key=' + urllib.parse.quote(public_link)
            response = requests.get(list_api_link)
            print(response)

            if response.status_code == 200:
                data = response.json()
                items = data.get('_embedded', {}).get('items', [])

                print("Список файлов и папок:")
                for item in items:
                    print(f"Название: {item['name']}, Тип: {item['type']}, Размер: {item.get('size', 'N/A')} байт")
            else:
                print("Ошибка при получении данных:", response.status_code)

        return context
