from django.views.generic import TemplateView
import requests
import urllib

element_types = {
    "dir": 'папка',
    "file": 'файл'
}
general_download_api_link = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='
general_list_api_link = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='

class MainView(TemplateView):
    template_name = 'index.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        # получение файлов публичной ссылки
        if 'link' in self.request.GET:
            public_link = self.request.GET['link']
            response = requests.get(public_link)
            print(response)

            # ссылка на просмотр
            list_api_link = general_list_api_link + urllib.parse.quote(public_link)
            response = requests.get(list_api_link)
            print(response)

            if response.status_code == 200:
                data = response.json()
                items = data.get('_embedded', {}).get('items', [])

                print()
                for item in items:
                    type = element_types[item['type']]
                    print(f"public_key: {item['public_key']}, {type} {item['name']}")
            else:
                print("Ошибка при получении данных:", response.status_code)

        return context
