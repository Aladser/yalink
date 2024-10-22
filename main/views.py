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
            link = self.request.GET['link']
            response = requests.get(link, allow_redirects=True)
            print(link)
            print(response)

        return context
