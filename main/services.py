import urllib

import requests

element_types = {
    "dir": 'Папка',
    "file": 'Файл'
}
general_download_api_link_start = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='
"""начало ссылки на скачивание файла"""

def get_elements_of_public_link(public_link: str, response_data: dict) -> list:
    """
    Возвращает список папок и файлов общего ресурса Яндекс Диска.
    :param public_link: публичная ссылка
    :param download_api_link: ссылка на загрузку публичного ресурса.
    :param response_data: ответ запроса на просмотр публичного ресурса
    """

    download_api_link = general_download_api_link_start + urllib.parse.quote(public_link)
    """ссылка на загрузку публичной яндекс ссылки"""

    items_list = []
    if response_data.get('type') == 'file':
        # открывается публичный файл
        items_list.append({'name': response_data.get('name'), 'url': response_data.get('file')})
    else:
        # открывается публичная папка
        items = response_data.get('_embedded', {}).get('items', [])
        for item in items:
            elem_name = f"{element_types[item['type']]} {item['name']}"

            if item['type'] == 'file':
                get_elem_download_url = f"{download_api_link}&path={item['path']}"
                get_elem_download_url_data = requests.get(get_elem_download_url)
                elem_link = get_elem_download_url_data.json()['href']
                elem_type = item.get('media_type')
            else:
                elem_link = '/?link=' + public_link + '&path=' + urllib.parse.quote(item['path'])
                elem_type = 'Папка'
            items_list.append({'name': elem_name, 'url': elem_link, 'type': elem_type})

    return items_list

