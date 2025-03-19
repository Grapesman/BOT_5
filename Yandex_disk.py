import requests
# Функция для получения файла с Яндекс-Диска
async def download_file_from_yandex_disk(token, directory, save_path):
    url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path={directory}'
    headers = {'Authorization': f'OAuth {token}'}
    # Получаем ссылку для скачивания файла
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        download_url = response.json().get('href')
        # Скачиваем файл по полученной ссылке
        file_response = requests.get(download_url)
        with open(save_path, 'wb') as f:
            f.write(file_response.content)
        print(f'Файл загружен и сохранён как {save_path}')
    else:
        raise Exception(f'Ошибка при получении файла: {response.text}')