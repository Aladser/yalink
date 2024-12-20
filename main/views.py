import os

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from libs.managed_cache import ManagedCache
from libs.yandex_api_service import YandexAPIService


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
        context['prev_url'] = None
        context["search_url"] = os.getenv("DEFAULT_SEARCH_URL") or ""
        if not 'link' in self.request.GET:
            return context

        if not YandexAPIService.is_valid_public_url(self.request.GET['link']):
            context['error'] = "Ссылка не является публичной ссылкой на Яндекс диск"
            return context

        public_link = context["search_url"] = self.request.GET['link']
        """ссылка на общедоступный Яндекс ресурс"""
        public_link_path = None
        """путь элемента ссылки"""

        if 'path' in self.request.GET:
            public_link_path = self.request.GET['path']
            # ссылка на папку выше, если находимся внутри папки ресурса
            prev_path_list = self.request.GET['path'].split('/')[:-1]
            prev_path = '/'.join(prev_path_list)
            context['prev_url'] = f"?link={self.request.GET['link']}"
            if prev_path != '':
                context['prev_url'] += f"&path={'/'.join(prev_path_list)}"
        else:
            context['prev_url'] = False

        # --- Получение из КЭШа ---
        cache_key = public_link + public_link_path if public_link_path else public_link
        cached_data = ManagedCache.get_data(cache_key)
        if cached_data:
            context['items'], context['types'] = cached_data['items'], cached_data['types']
            context['resource_download_link'] = cached_data['resource_download_link']
            context['is_items'] = len(context['items']) > 0
            return context

        yadi_request_data = YandexAPIService.get_elements_of_yadisk_public_link(public_link, public_link_path)
        if yadi_request_data['code'] == 200:
            data = yadi_request_data['data']
            context['types'] = ['Все'] + sorted(list(set(item['type'] for item in data)))
            context['items'] = data
            context['is_items'] = len(data) > 0
            resource_download_link = YandexAPIService.get_yadisk_resource_download_link(public_link)
            context['resource_download_link'] = resource_download_link

            ManagedCache.save_data(
                cache_key,
                {
                    "items": data,
                    "types": context['types'],
                    'resource_download_link': resource_download_link
                }
            )
        else:
            context["error"] = yadi_request_data['data']

        return context
