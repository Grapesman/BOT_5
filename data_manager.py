import os
from datetime import datetime

import asyncio
import requests
from openpyxl import load_workbook, Workbook

import settings


class YandexManager:
    yandex_locker = asyncio.Lock()

    @classmethod
    async def download_excel_from_yandex(cls) -> bool:
        async with cls.yandex_locker:
            url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path={settings.YA_FILE_PATH}'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                download_url = response.json().get('href')
                file_response = requests.get(download_url)
                with open(settings.FILE_SAVE_PATH, 'wb') as f:
                    f.write(file_response.content)
                print(f'Файл загружен и сохранён как {settings.FILE_SAVE_PATH}')

            else:
                raise Exception(f'Ошибка при получении файла: {response.text}')

    @classmethod
    async def upload_excel_to_yandex(cls) -> bool:
        async with cls.yandex_locker:
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Authorization': f'OAuth {settings.YA_TOKEN}'}
            params = {'path': settings.YA_FILE_PATH, 'overwrite': 'true'}

            # Запрос для получения ссылки для загрузки
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f'Ошибка получения ссылки для загрузки: {response.json()}')
                return False

            upload_url = response.json().get('href')

            # Загружаем файл
            with open(settings.FILE_SAVE_PATH, 'rb') as file:
                response = requests.put(upload_url, files={'file': file})
            if response.status_code == 201:
                print('Файл успешно загружен на Яндекс Диск.')
                return True
            else:
                print(f'Ошибка при загрузке файла: {response.json()}')
                return False


class ExcelManager:
    excel_locker = asyncio.Lock()

    @classmethod
    async def get_excel_book(cls) -> Workbook:
        async with cls.excel_locker:
            book = load_workbook(settings.FILE_SAVE_PATH)
            return book

    @classmethod
    async def add_new_article_in_excel(
            cls,
            book: Workbook,
            title: str,
            date: str,
            thesis: str,
            authors: str,
            keywords: str
    ):
        async with cls.excel_locker:
            sheet = book['Каталог статей']

            string_qty = 1
            while sheet['A' + str(string_qty + 1)].value is not None:
                string_qty += 1

            today = datetime.today()
            today_date = today.strftime("%d.%m.%Y")

            sheet['A' + str(string_qty + 1)].value = str(string_qty)
            sheet['B' + str(string_qty + 1)].value = title
            sheet['D' + str(string_qty + 1)].value = date
            sheet['F' + str(string_qty + 1)].value = thesis
            sheet['H' + str(string_qty + 1)].value = authors
            sheet['J' + str(string_qty + 1)].value = keywords
            sheet['C' + str(string_qty + 1)].value = datetime.strptime(today_date, "%d.%m.%Y")

            book.save(settings.FILE_SAVE_PATH)
            print("Данные успешно записаны в файл")


class DataManager:
    data_locker = asyncio.Lock()

    @classmethod
    async def get_excel_from_yandex(cls) -> Workbook:
        async with cls.data_locker:
            await YandexManager.download_excel_from_yandex()
            book = await ExcelManager.get_excel_book()
            os.remove(settings.FILE_SAVE_PATH)
        return book

    @classmethod
    async def add_new_article_in_yandex(
            cls,
            title: str,
            date: str,
            thesis: str,
            authors: str,
            keywords: str
    ):
        async with cls.data_locker:
            await YandexManager.download_excel_from_yandex()
            book = await ExcelManager.get_excel_book()
            await ExcelManager.add_new_article_in_excel(book, title, date, thesis, authors, keywords)
            uploaded: bool = await YandexManager.upload_excel_to_yandex()
            os.remove(settings.FILE_SAVE_PATH)
        return uploaded