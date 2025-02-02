import requests
global UpLOAD
async def upload_file_to_yandex_disk(oauth_token, file_path, disk_path):
    global UpLOAD
    UpLOAD = False
    # Получаем URL для загрузки
    url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {
        'Authorization': f'OAuth {oauth_token}'
    }

    # Параметры запроса
    params = {
        'path': disk_path,  # Путь на Яндекс Диске, куда будет загружен файл
        'overwrite': 'true'  # Перезаписать файл, если он существует
    }

    # Запрос для получения ссылки для загрузки
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f'Ошибка получения ссылки для загрузки: {response.json()}')
        return

    upload_url = response.json().get('href')

    # Загружаем файл
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, files={'file': file})

    if response.status_code == 201:
        print('Файл успешно загружен на Яндекс Диск.')
        UpLOAD = True
    else:
        print(f'Ошибка при загрузке файла: {response.json()}')
