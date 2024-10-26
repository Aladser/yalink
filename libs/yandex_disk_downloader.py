import urllib
import requests


class YandexDiskDownloader:
    """Загрузчик файлов Яндекс Диска"""

    list_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources?public_key='
    """начало ссылки на просмотр файлов"""
    general_download_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='
    """начало ссылки на скачивание файла"""
    element_types = {
        "dir": 'Папка',
        "file": 'Файл'
    }

    @staticmethod
    def get_elements_of_public_link(public_link: str, path: str | None = None) -> dict:
        """
        Возвращает список папок и файлов
        :param public_link: публичная ссылка
        :param path: относительный путь элемента ссылки
        :return: {код ответа, данные}
        """

        decoded_public_link = urllib.parse.quote(public_link)
        list_api_link = YandexDiskDownloader.list_api_link_start + decoded_public_link
        """ссылка на просмотр содержимого"""
        if path:
            list_api_link += f"&path={path}"
        download_api_link = YandexDiskDownloader.general_download_api_link_start + decoded_public_link
        """ссылка на загрузку"""

        # проверка ссылки просмотра файлов
        response = requests.get(list_api_link)
        if response.status_code == 404:
            return {'code': response.status_code, "data": "Ссылка не найдена"}
        elif response.status_code == 500:
            return {'code': response.status_code, "data": "Неправильная ссылка"}
        elif response.status_code != 200:
            return {'code': response.status_code, "data": f"Ошибка. Код ошибки {str(response.status_code)}"}

        items_list = []
        response_data = response.json()
        if response_data.get('type') == 'file':
            # открывается публичный файл
            items_list.append({'name': response_data.get('name'), 'url': response_data.get('file')})
        else:
            # открывается публичная папка
            items = response_data.get('_embedded', {}).get('items', [])
            for item in items:
                elem_name = f"{YandexDiskDownloader.element_types[item['type']]} {item['name']}"

                if item['type'] == 'file':
                    get_elem_download_url = f"{download_api_link}&path={item['path']}"
                    get_elem_download_url_data = requests.get(get_elem_download_url)
                    elem_link = get_elem_download_url_data.json()['href']
                    elem_type = item.get('media_type')
                else:
                    elem_link = '/?link=' + public_link + '&path=' + urllib.parse.quote(item['path'])
                    elem_type = 'Папка'
                items_list.append({'name': elem_name, 'url': elem_link, 'type': elem_type})

        return {'code': 200, "data": items_list}

    def get_resource_download_link(public_link: str) -> str | None:
        """
        Возвращает ссылку на скачивание ресурса
        """

        decoded_public_link = urllib.parse.quote(public_link)
        download_link = YandexDiskDownloader.general_download_api_link_start + decoded_public_link
        download_link_request_response = requests.get(download_link)
        if download_link_request_response.status_code == 200:
            return download_link_request_response.json()['href']
        else:
            raise None
