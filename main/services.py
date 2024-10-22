import requests

element_types = {
    "dir": 'Папка',
    "file": 'Файл'
}


def get_shared_files_from_public_link(download_api_link: str, response_data: str) -> list:
    """Возвращает список загрузочных ссылок файлов"""

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
            items_list.append({'name': elem_name, 'url': download_link})

    return items_list