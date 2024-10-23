import requests

element_types = {
    "dir": 'Папка',
    "file": 'Файл'
}


def get_shared_files_from_public_link(download_api_link: str, response_data: dict) -> list:
    """
    Возвращает список файлов и папок общего ресурса Яндекс Диска
    :param download_api_link: ссылка на скачивание ресурса
    :param response_data: данные запроса на просмотр ресурса
    :return: список файлов и папок ресурса
    """

    items_list = []

    if response_data.get('type') == 'file':
        # открывается публичный файл

        items_list.append({'name': response_data.get('name'), 'url': response_data.get('file')})
    else:
        # открывается публичная папка

        items = response_data.get('_embedded', {}).get('items', [])
        for item in items:
            elem_name = f"{element_types[item['type']]} {item['name']}"

            get_elem_download_url = f"{download_api_link}&path={item['path']}"
            get_elem_download_url_data = requests.get(get_elem_download_url)
            download_link = get_elem_download_url_data.json()['href']
            elem_type = item.get('media_type') if item.get('media_type') is not None else "Папка"
            items_list.append({'name': elem_name, 'url': download_link, 'type': elem_type})

    return items_list
