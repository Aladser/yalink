from http.client import responses

from celery.worker.state import requests
from django.views.generic import TemplateView


class MainView(TemplateView):
    extra_context = {
    }
    template_name = 'index.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        # получение файлов публичной ссылки
        if 'link' in self.request.GET:
            public_link = self.request.GET['link']
            print(f"Сcылка: {public_link}")

            direct_link = public_link.replace('https://disk.yandex.ru/d/',
                                              'https://downloader.disk.yandex.ru/disk/').replace('https://', 'https://')

            response = requests.get(direct_link)
            print(response)

        return context
